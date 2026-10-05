import { describe, expect, it } from 'vitest'
import {
  againToday, applyEvent, emptyInbox, fsrsDay, isEvent, isInbox, liveEvents, mergeInbox, serializeInbox,
  INBOX_PATH, type Inbox, type InboxEvent, type ReviewRow, type SchedRow,
} from '../inbox'
import { review } from '../fsrs'
import { InvalidRemoteError, StaleError, syncDocs, type DocSpec, type Remote, type RemoteFile, type SyncTarget } from '../sync'
import { AuthError, githubRemote, readQuery, toBase64, type RepoConfig } from '../github'

let n = 0
const ev = (x: Partial<InboxEvent> = {}): InboxEvent => ({
  eid: `e${++n}`, ts: 1000 + n, date: '2026-10-04', deck: 'problems', id: 1, op: 'rate', rating: 3, ...x,
})

describe('事件格式', () => {
  it('校验规则和 dashboard/inbox.py 的 valid() 一致', () => {
    expect(isEvent(ev())).toBe(true)
    expect(isEvent(ev({ deck: 'syntax', id: 'str/标题' }))).toBe(true)
    expect(isEvent(ev({ id: '1' }))).toBe(false)                          // 题号必须是整数
    expect(isEvent(ev({ deck: 'syntax', id: 3 }))).toBe(false)
    expect(isEvent(ev({ rating: 5 as never }))).toBe(false)
    expect(isEvent(ev({ op: 'comment', rating: undefined, text: '  ' }))).toBe(false)
    expect(isEvent(ev({ op: 'comment', rating: undefined, text: '干扰项能 AC' }))).toBe(true)
    expect(isEvent(ev({ op: 'nope' as never }))).toBe(false)
  })

  it('合并 = 按 eid 取并集, 和顺序无关; 已经落进 main 的扔掉', () => {
    const [a1, a2, b1] = [ev(), ev(), ev()]
    const a: Inbox = { events: [a2, a1] }, b: Inbox = { events: [b1, a1] }
    expect(mergeInbox(a, b).events.map((e) => e.eid)).toEqual([a1.eid, a2.eid, b1.eid])
    expect(serializeInbox(mergeInbox(a, b))).toBe(serializeInbox(mergeInbox(b, a)))
    expect(mergeInbox(a, b, new Set([a1.eid])).events.map((e) => e.eid)).toEqual([a2.eid, b1.eid])
  })

  it('输出一行一条, 读回来不变', () => {
    const v = mergeInbox(emptyInbox(), { events: [ev(), ev({ op: 'comment', rating: undefined, text: '中文' })] })
    const s = serializeInbox(v)
    expect(s.split('\n')).toHaveLength(5)                                    // 头 + 2 条 + 尾 + 末尾换行
    expect(isInbox(JSON.parse(s))).toBe(true)
    expect(JSON.parse(s)).toEqual(v)
    expect(serializeInbox(emptyInbox())).toBe('{"events": []}\n')
  })

  it('坏掉的单条在读的时候跳过', () => {
    const good = ev()
    expect(liveEvents({ events: [good, { eid: 'x' } as never] }, new Set())).toEqual([good])
  })
})

describe('重放', () => {
  const row = (x: Partial<SchedRow> = {}): SchedRow => ({ id: 1, fsrs: {}, due: '', ...x })

  it('评分: 新卡用 fsrs.ts 算, 行上的调度字段跟着变, 返回 reviews.jsonl 那一行', () => {
    const rows = [row()]
    const r = applyEvent(rows, ev({ rating: 3 })) as ReviewRow
    const want = review(null, 3, '2026-10-04')
    expect(rows[0].due).toBe(want.card.due)
    expect(rows[0].last_review).toBe('2026-10-04')
    expect(rows[0].reps).toBe(1)
    expect(r).toMatchObject({ id: 1, rating: 3, state: 'new', elapsed_days: null, interval: want.interval, src: 'sync' })
    expect(r.deck).toBeUndefined()                                           // 题目牌组的老口径: 不写 deck
  })

  it('事件晚到(本机之后又评过): 按上次复习那天算, 不出负间隔', () => {
    expect(fsrsDay('2026-10-01', '2026-10-03')).toBe('2026-10-03')
    expect(fsrsDay('2026-10-04', '2026-10-03')).toBe('2026-10-04')
    const card = review(null, 3, '2026-10-03').card
    const rows = [row({ fsrs: card })]
    const r = applyEvent(rows, ev({ date: '2026-10-01', rating: 4 }))!
    expect(r.date).toBe('2026-10-01')                                        // 日志里还是手机上那天
    expect(r.elapsed_days).toBe(0)
    expect(rows[0].due).toBe(review(card, 4, '2026-10-03').card.due)
  })

  it('暂停只记一次开始日期; 语法卡没有暂停; 找不到卡就跳过', () => {
    const rows = [row()]
    applyEvent(rows, ev({ op: 'pause', rating: undefined, date: '2026-10-02' }))
    applyEvent(rows, ev({ op: 'pause', rating: undefined, date: '2026-10-03' }))
    expect(rows[0].paused).toBe('2026-10-02')
    const syn = [row({ id: 'a/b' })]
    applyEvent(syn, ev({ deck: 'syntax', id: 'a/b', op: 'pause', rating: undefined }))
    expect(syn[0].paused).toBeUndefined()
    expect(applyEvent(rows, ev({ id: 99 }))).toBeNull()
  })

  it('今天最后一次评 1 的再问一遍(同 server.review_carry)', () => {
    const rv = (id: number, rating: number, ts: number, date = '2026-10-04', deck?: 'syntax') =>
      ({ id, rating, ts, date, ...(deck ? { deck } : {}) }) as ReviewRow
    const rows = [rv(1, 1, 1), rv(2, 1, 2), rv(2, 3, 3), rv(3, 1, 4, '2026-10-03'), rv(4, 1, 5, '2026-10-04', 'syntax')]
    expect(againToday(rows, 'problems', '2026-10-04')).toEqual([1])
    expect(againToday(rows, 'syntax', '2026-10-04')).toEqual([4])
  })
})

// ---------------------------------------------------------------- 同步 ----
// 下面两组照搬 ai-infra-inferview 的 sync.test.ts, 数据换成这边的事件 inbox

const spec: DocSpec<Inbox> = {
  path: INBOX_PATH, label: '复习', empty: emptyInbox, validate: isInbox,
  merge: (a, b) => mergeInbox(a, b), serialize: serializeInbox,
}

function fakeRemote(initial: Record<string, string | null> = {}) {
  const files: Record<string, string | null> = { ...initial }
  let version = 0
  const writes: RemoteFile[][] = []
  const remote: Remote & { files: typeof files; writes: typeof writes; bump: (p: string, t: string) => void } = {
    files, writes,
    bump(p, t) { files[p] = t; version++ },
    async read(paths) {
      return { texts: Object.fromEntries(paths.map((p) => [p, files[p] ?? null])), version: String(version) }
    },
    async write(changes, v) {
      if (v !== String(version)) throw new StaleError()
      writes.push(changes)
      for (const c of changes) files[c.path] = c.text
      version++
    },
  }
  return remote
}

function target(initial: Inbox) {
  const box = { value: initial }
  const t: SyncTarget<Inbox> = { spec, get: () => box.value, set: (v) => (box.value = v) }
  return { t, box }
}

describe('syncDocs', () => {
  it('远端没有文件时写上去; 再同步一次没有变化就不写', async () => {
    const remote = fakeRemote()
    const { t } = target({ events: [ev()] })
    expect((await syncDocs(remote, [t])).written).toEqual([INBOX_PATH])
    expect((await syncDocs(remote, [t])).written).toEqual([])
    expect(remote.writes).toHaveLength(1)
  })

  it('两台设备的事件都留下', async () => {
    const theirs = ev()
    const remote = fakeRemote({ [INBOX_PATH]: serializeInbox({ events: [theirs] }) })
    const mine = ev()
    const { t, box } = target({ events: [mine] })
    await syncDocs(remote, [t])
    expect(box.value.events.map((e) => e.eid)).toEqual([theirs.eid, mine.eid])
    expect(JSON.parse(remote.files[INBOX_PATH]!)).toEqual(box.value)
  })

  it('写之前别的设备先提交了: 重读、重合并、再写', async () => {
    const remote = fakeRemote()
    const { t } = target({ events: [ev()] })
    const read = remote.read.bind(remote)
    let raced = false
    remote.read = async (paths) => {
      const snap = await read(paths)
      if (!raced) { raced = true; remote.bump(INBOX_PATH, serializeInbox({ events: [ev()] })) }
      return snap
    }
    const r = await syncDocs(remote, [t])
    expect(r.retries).toBe(1)
    expect(JSON.parse(remote.files[INBOX_PATH]!).events).toHaveLength(2)
  })

  it('远端文件格式不对时不覆盖', async () => {
    const remote = fakeRemote({ [INBOX_PATH]: '{ broken' })
    await expect(syncDocs(remote, [target({ events: [ev()] }).t])).rejects.toBeInstanceOf(InvalidRemoteError)
    expect(remote.files[INBOX_PATH]).toBe('{ broken')
  })
})

describe('github remote', () => {
  const repo: RepoConfig = { owner: 'o', name: 'r', branch: 'data' }
  const paths = [INBOX_PATH]

  function fakeFetch(responses: { status?: number; body: unknown }[]) {
    const calls: { query: string; variables: any }[] = []           // eslint-disable-line @typescript-eslint/no-explicit-any
    const fn = async (_url: string, init: RequestInit) => {
      calls.push(JSON.parse(init.body as string))
      const r = responses.shift()!
      return new Response(JSON.stringify(r.body), { status: r.status ?? 200 })
    }
    return { fn, calls }
  }
  const commit = (oid: string, texts: (string | null)[]) => ({
    oid, ...Object.fromEntries(texts.map((t, i) => [`f${i}`, t === null ? null : { object: { text: t } }])),
  })

  it('base64 能编码中文', () => {
    const s = '语法卡 ✎ hello'
    expect(new TextDecoder().decode(Uint8Array.from(atob(toBase64(s)), (c) => c.charCodeAt(0)))).toBe(s)
  })

  it('读查询给文件起别名', () => {
    expect(readQuery(paths)).toContain(`f0: file(path: "${INBOX_PATH}")`)
  })

  it('数据分支不存在: 从默认分支建出来', async () => {
    const { fn, calls } = fakeFetch([
      { body: { data: { repository: { id: 'R', defaultBranchRef: { target: commit('main1', [null]) }, ref: null } } } },
      { body: { data: { createRef: { ref: { name: 'data' } } } } },
    ])
    const snap = await githubRemote({ token: 't', repo, fetch: fn }).read(paths)
    expect(snap).toEqual({ version: 'main1', texts: { [INBOX_PATH]: null } })
    expect(calls[1].variables.input).toEqual({ repositoryId: 'R', name: 'refs/heads/data', oid: 'main1' })
  })

  it('写: 一个 commit, 带期望的 head', async () => {
    const { fn, calls } = fakeFetch([{ body: { data: { createCommitOnBranch: { commit: { oid: 'd2' } } } } }])
    await githubRemote({ token: 't', repo, fetch: fn, device: 'iPhone' }).write([{ path: INBOX_PATH, text: '{}\n' }], 'd1', '复习')
    const input = calls[0].variables.input
    expect(input.expectedHeadOid).toBe('d1')
    expect(input.message.headline).toBe('sync: 复习 · iPhone')
  })

  it('head 对不上 -> StaleError, 401 -> AuthError', async () => {
    const stale = fakeFetch([{ body: { errors: [{ type: 'STALE_DATA', message: 'Expected branch to point to "d0"' }] } }])
    await expect(githubRemote({ token: 't', repo, fetch: stale.fn }).write([{ path: 'a', text: 'b' }], 'd0', 'x')).rejects.toBeInstanceOf(StaleError)
    const auth = fakeFetch([{ status: 401, body: { message: 'Bad credentials' } }])
    await expect(githubRemote({ token: 't', repo, fetch: auth.fn }).read(paths)).rejects.toBeInstanceOf(AuthError)
  })
})
