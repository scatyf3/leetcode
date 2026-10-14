import { reactive } from 'vue'
import { api } from './api'
import { todayStr } from './lib/dates'
import { AuthError, DATA_REPO, canWrite, checkToken, githubRemote } from './lib/github'
import {
  INBOX_PATH, emptyInbox, isInbox, liveEvents, mergeInbox, serializeInbox,
  type Inbox, type InboxEvent,
} from './lib/inbox'
import { InvalidRemoteError, syncDocs, type DocSpec, type SyncTarget } from './lib/sync'

/**
 * 只读站(GitHub Pages)上的复习记录同步。照着 ai-infra-inferview 的 docs/.vitepress/theme/sync.ts,
 * 差别是这边只有一份数据 —— 复习事件(见 lib/inbox.ts), 并且只在**只读站**上启用:
 * 本地 server.py 那份看板直接写真相源, 用不着它。
 *
 * - 没连 token: 和以前一样纯自测, 不记录(off)。
 * - 连了 token(github): 评分 / 暂停 / 批注记成事件, 先存 localStorage(界面立刻更新、离线不丢),
 *   停手 2 秒、切到后台、重新联网时推到 data 分支。本机 server.py 再拉下来落盘(dashboard/inbox.py)。
 *
 * 页面上的数据 = 导出时 main 的状态 + 还没落进 main 的事件重放一遍(app.js 的 applyPending)。
 * 「落进 main 了没有」看导出的账本 api/sync-applied.json —— 落了的从 inbox 里删掉, 也不再重放。
 */

export type SyncMode = 'off' | 'github'
export type SyncStatus = 'idle' | 'syncing' | 'offline' | 'error'

export const syncState = reactive({
  mode: 'off' as SyncMode,
  status: 'idle' as SyncStatus,
  /** 本机有事件还没推上去 */
  pending: false,
  lastSync: 0,
  error: '',
  login: '',
  /** 还没落进 main 的事件数(推上去了但本机 server 还没拉的也算) */
  waiting: 0,
})

export const DATA_BRANCH_URL = `https://github.com/${DATA_REPO.owner}/${DATA_REPO.name}/blob/${DATA_REPO.branch}/${INBOX_PATH}`

const TOKEN_KEY = 'lc:gh-token'
const LOGIN_KEY = 'lc:gh-login'
const PENDING_KEY = 'lc:sync-pending'
const LOCAL_KEY = 'lc:sync-inbox:v1'

/** 停手多久后同步: 每次同步是 data 分支上的一个 commit, 攒一攒 */
const DEBOUNCE = 2000
const RETRY_MS = 30_000
/** 前台时多久拉一次别的设备的事件 */
const POLL_MS = 120_000

const ls = {
  get(k: string): string | null {
    try { return localStorage.getItem(k) } catch { return null }
  },
  set(k: string, v: string) {
    try { localStorage.setItem(k, v) } catch { /* 隐私模式 */ }
  },
  del(k: string) {
    try { localStorage.removeItem(k) } catch { /* 隐私模式 */ }
  },
}

/** 已经落进 main 的 eid(导出的账本)。initSync 里拉 */
let applied = new Set<string>()
let doc: Inbox = emptyInbox()
let onRemote: () => void = () => {}

function saveLocal() {
  ls.set(LOCAL_KEY, serializeInbox(doc))
  syncState.waiting = liveEvents(doc, applied).length
}

function setPending(v: boolean) {
  syncState.pending = v
  v ? ls.set(PENDING_KEY, '1') : ls.del(PENDING_KEY)
}

function deviceName(): string {
  const ua = navigator.userAgent
  if (/iPhone/.test(ua)) return 'iPhone'
  if (/iPad/.test(ua)) return 'iPad'
  if (/Android/.test(ua)) return 'Android'
  return '桌面'
}

// ---------- 同步调度(同 ai-infra-inferview) ----------

const spec: DocSpec<Inbox> = {
  path: INBOX_PATH,
  label: '复习',
  empty: emptyInbox,
  validate: isInbox,
  merge: (a, b) => mergeInbox(a, b, applied),
  serialize: serializeInbox,
}

const target: SyncTarget<Inbox> = {
  spec,
  get: () => doc,
  set(v) {
    const known = new Set(doc.events.map((e) => e.eid))
    const fresh = v.events.some((e) => !known.has(e.eid))
    doc = v
    saveLocal()
    if (fresh) onRemote()                 // 别的设备评过的: 让看板重放一遍
  },
}

let version = 0
let timer: ReturnType<typeof setTimeout> | undefined
let running: Promise<void> | null = null
let again = false
let lastAttempt = 0

function schedule(delay: number) {
  clearTimeout(timer)
  timer = setTimeout(() => void runSync(), delay)
}

async function runSync(keepalive = false): Promise<void> {
  if (running) {
    again = true
    return running
  }
  const token = ls.get(TOKEN_KEY)
  if (syncState.mode !== 'github' || !token) return
  if (!navigator.onLine) {
    syncState.status = 'offline'
    return
  }
  const remote = githubRemote({ token, device: deviceName() })
  remote.keepalive = keepalive
  lastAttempt = Date.now()
  const startVersion = version
  syncState.status = 'syncing'
  let ok = false
  running = (async () => {
    try {
      await syncDocs(remote, [target])
      ok = true
      syncState.status = 'idle'
      syncState.error = ''
      syncState.lastSync = Date.now()
      if (version === startVersion) setPending(false)
      else again = true
    } catch (e) {
      console.error('[sync]', e)
      syncState.status = 'error'
      syncState.error = (e as Error).message
      if (!(e instanceof AuthError || e instanceof InvalidRemoteError)) schedule(RETRY_MS)
    } finally {
      running = null
    }
  })()
  await running
  if (ok && again) {
    again = false
    schedule(DEBOUNCE)
  }
}

function pull(minGapMs: number) {
  if (Date.now() - lastAttempt >= minGapMs) schedule(0)
}

// ---------- 启动 ----------

let readyP: Promise<void> | null = null

/**
 * 只读站启动时调一次。拉账本、读本地缓存、开始同步。
 * onRemoteEvents: 从远端拿到了本机没见过的事件(别的设备评的), 看板该重放一遍了。
 */
export function initSync(onRemoteEvents: () => void): Promise<void> {
  if (readyP) return readyP
  onRemote = onRemoteEvents
  readyP = (async () => {
    try {
      applied = new Set(((await api('/api/sync-applied')).eids as string[]) || [])
    } catch { applied = new Set() }
    let local: unknown = null
    try { local = JSON.parse(ls.get(LOCAL_KEY) || 'null') } catch { local = null }
    doc = mergeInbox(emptyInbox(), isInbox(local) ? local : emptyInbox(), applied)
    saveLocal()

    const token = ls.get(TOKEN_KEY)
    syncState.mode = token ? 'github' : 'off'
    syncState.login = token ? ls.get(LOGIN_KEY) ?? '' : ''
    syncState.pending = ls.get(PENDING_KEY) === '1'

    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') pull(5_000)
      // 切到后台(手机锁屏、切 app): 有没推上去的就赶紧推
      else if (syncState.pending) void runSync(true)
    })
    window.addEventListener('pagehide', () => { if (syncState.pending) void runSync(true) })
    window.addEventListener('focus', () => pull(15_000))
    window.addEventListener('online', () => schedule(0))
    window.addEventListener('offline', () => { if (syncState.mode === 'github') syncState.status = 'offline' })
    setInterval(() => { if (document.visibilityState === 'visible') pull(POLL_MS) }, POLL_MS)

    schedule(0)
  })()
  return readyP
}

// ---------- 给看板 / 复习面板用的 ----------

/** 连上 GitHub 才记录。没连的只读站照旧是纯自测 */
export const canRecord = () => syncState.mode === 'github'

/** 还没落进 main 的事件, 按发生顺序。看板拿它在导出的数据上重放 */
export const pendingEvents = (): InboxEvent[] => liveEvents(doc, applied)

let seq = 0
function newEid(): string {
  try { return crypto.randomUUID().replace(/-/g, '').slice(0, 16) } catch { /* 非 https */ }
  return Date.now().toString(36) + (++seq).toString(36) + Math.random().toString(36).slice(2, 8)
}

/** 记一条事件(存本地 + 排队推上去), 返回补全了 eid / 时间的那条 */
export function record(e: Pick<InboxEvent, 'deck' | 'id' | 'op'> & Partial<InboxEvent>): InboxEvent {
  const ev: InboxEvent = {
    ...e,
    eid: newEid(),
    ts: Math.floor(Date.now() / 1000),
    date: todayStr(),
    device: deviceName(),
  }
  doc = mergeInbox(doc, { events: [ev] }, applied)
  version++
  saveLocal()
  setPending(true)
  schedule(DEBOUNCE)
  return ev
}

export function syncNow() {
  schedule(0)
}

/** 验证并保存 token; 不合格时抛错, 原来的模式不变 */
export async function connectGitHub(token: string): Promise<void> {
  token = token.trim()
  const info = await checkToken(token)
  if (!canWrite(info.permission)) {
    throw new Error(`token 能登录(${info.login}), 但没有 ${DATA_REPO.owner}/${DATA_REPO.name} 的写权限`)
  }
  ls.set(TOKEN_KEY, token)
  ls.set(LOGIN_KEY, info.login)
  syncState.mode = 'github'
  syncState.login = info.login
  syncState.error = ''
  syncState.status = 'idle'
  setPending(true)
  schedule(0)
}

export function disconnectGitHub() {
  ls.del(TOKEN_KEY)
  ls.del(LOGIN_KEY)
  syncState.mode = 'off'
  syncState.login = ''
  syncState.error = ''
  syncState.status = 'idle'
}
