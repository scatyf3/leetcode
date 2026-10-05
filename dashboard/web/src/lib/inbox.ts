// 只读站上的复习记录: 一条条**只追加**的事件, 同步到仓库 data 分支的 dashboard/sync-inbox.json,
// 本机 server.py 再把它们落回 meta.json / syntax/state.json / reviews.jsonl(见 dashboard/inbox.py)。
//
// 为什么记事件而不是像 ai-infra-inferview 那样同步整份状态: 这边的调度状态散在一百多个
// meta.json 里, 本机看板同时也在评分。事件不可变, 合并就是按 eid 取并集, 谁先谁后都一样;
// FSRS 由 fsrs.py 统一重放, 手机上用 ./fsrs.ts 算出来的只是落回去之前的临时显示。
import { review, newCard, type Card, type Rating } from './fsrs'
import type { Deck } from './types'

export const INBOX_PATH = 'dashboard/sync-inbox.json'   // dashboard/inbox.py 的 INBOX_PATH

export type Op = 'rate' | 'pause' | 'comment'

export interface InboxEvent {
  /** 随机 id。去重、账本、批注的 cid 都用它 */
  eid: string
  /** 秒 */
  ts: number
  /** 手机上的本地日期 —— 评分按这天算, reviews.jsonl 的 date 也记这天 */
  date: string
  deck: Deck
  /** 题号(整数) / 语法卡 id("主题/标题") */
  id: number | string
  op: Op
  rating?: Rating
  /** 批注: 卡标题(给 agent 看) + 内容 */
  title?: string
  text?: string
  device?: string
}

export interface Inbox {
  events: InboxEvent[]
}

/** 和 dashboard/inbox.py 的 valid() 同一套口径 */
export function isEvent(e: unknown): e is InboxEvent {
  if (!e || typeof e !== 'object') return false
  const x = e as Record<string, unknown>
  if (typeof x.eid !== 'string' || !x.eid) return false
  if (!['rate', 'pause', 'comment'].includes(x.op as string)) return false
  if (x.deck !== 'problems' && x.deck !== 'syntax') return false
  if (typeof x.ts !== 'number' || typeof x.date !== 'string') return false
  if (x.deck === 'problems' ? !Number.isInteger(x.id) : typeof x.id !== 'string') return false
  if (x.op === 'rate' && ![1, 2, 3, 4].includes(x.rating as number)) return false
  if (x.op === 'comment' && !String(x.text ?? '').trim()) return false
  return true
}

/** 文件整体的格式。单条坏了不算整份坏 —— 读的时候跳过那条(见 liveEvents) */
export const isInbox = (v: unknown): v is Inbox =>
  !!v && typeof v === 'object' && Array.isArray((v as Inbox).events)

export const emptyInbox = (): Inbox => ({ events: [] })

const byTime = (a: InboxEvent, b: InboxEvent) => a.ts - b.ts || (a.eid < b.eid ? -1 : a.eid > b.eid ? 1 : 0)

/**
 * 按 eid 取并集, 再扔掉已经落进 main 的(applied: 只读站导出的账本)。
 * 事件不可变, 所以同一个 eid 两边取哪份都一样。
 */
export function mergeInbox(a: Inbox, b: Inbox, applied: Set<string> = new Set()): Inbox {
  const m = new Map<string, InboxEvent>()
  for (const e of [...a.events, ...b.events]) {
    if (isEvent(e) && !applied.has(e.eid) && !m.has(e.eid)) m.set(e.eid, e)
  }
  return { events: [...m.values()].sort(byTime) }
}

/** 一行一条事件: data 分支上的 diff 读得懂, 也不会因为键序抖动产生空提交 */
export function serializeInbox(v: Inbox): string {
  const evs = [...v.events].sort(byTime)
  if (!evs.length) return '{"events": []}\n'
  return '{"events": [\n' + evs.map((e) => JSON.stringify(e)).join(',\n') + '\n]}\n'
}

/** 还没落进 main 的, 按发生顺序 */
export const liveEvents = (v: Inbox, applied: Set<string>) =>
  v.events.filter((e) => isEvent(e) && !applied.has(e.eid)).sort(byTime)

// ---------------------------------------------------------------- 重放 ----

/** 题目行 / 语法卡行里和调度有关的那几个字段(两边同形状, 见 server.list_problems / syntax.list_cards) */
export interface SchedRow {
  id: number | string
  fsrs?: Card | null
  due?: string | null
  stability?: number | null
  reps?: number | null
  last_review?: string | null
  fsrs_state?: string | null
  paused?: string | null
  [k: string]: unknown
}

/** 和 reviews.jsonl 一行同形状, 📈 进度和「今天评过 1 的再问一遍」都读它 */
export interface ReviewRow {
  ts: number
  date: string
  deck?: Deck
  id: number | string
  rating: Rating
  state: string
  elapsed_days: number | null
  stability: number | null
  difficulty: number | null
  new_stability: number
  new_difficulty: number
  interval: number
  due: string
  eid?: string
  src?: string
}

/** FSRS 按哪天算: server._fsrs_day 的同一条规则 —— 事件晚到时退到上次复习那天 */
export const fsrsDay = (evDate: string, lastReview?: string | null) =>
  (lastReview || '') > evDate ? (lastReview as string) : evDate

/**
 * 把一条事件就地放到行上(评分改调度字段, 暂停记日期)。批注不碰行。
 * 返回评分对应的 reviews.jsonl 行, 别的返回 null。找不到这张卡也返回 null ——
 * server 那边会记成 missing, 这边就当没发生。
 */
export function applyEvent(rows: SchedRow[], ev: InboxEvent): ReviewRow | null {
  const row = rows.find((r) => r.id === ev.id)
  if (!row) return null
  if (ev.op === 'pause') {
    if (ev.deck === 'problems' && !row.paused) row.paused = ev.date
    return null
  }
  if (ev.op !== 'rate' || !ev.rating) return null
  const before: Card = row.fsrs && Object.keys(row.fsrs).length ? row.fsrs : newCard()
  const day = fsrsDay(ev.date, before.last_review)
  const { card, interval } = review(before, ev.rating, day)
  row.fsrs = card
  row.due = card.due
  row.stability = card.stability
  row.reps = card.reps
  row.last_review = card.last_review
  row.fsrs_state = card.state
  const last = before.last_review
  return {
    ts: ev.ts,
    date: ev.date,
    ...(ev.deck === 'syntax' ? { deck: 'syntax' as Deck } : {}),
    id: ev.id,
    rating: ev.rating,
    state: before.state ?? 'new',
    elapsed_days: last ? Math.round((Date.parse(day) - Date.parse(last)) / 864e5) : null,
    stability: before.stability ?? null,
    difficulty: before.difficulty ?? null,
    new_stability: card.stability as number,
    new_difficulty: card.difficulty as number,
    interval,
    due: card.due as string,
    eid: ev.eid,
    src: 'sync',
  }
}

/** 今天、这个牌组里**最后一次**评分是 1 的 —— server.review_carry 的 again, 按时间排 */
export function againToday(reviews: ReviewRow[], deck: Deck, today: string): (number | string)[] {
  const last = new Map<number | string, number>()
  for (const r of [...reviews].sort((a, b) => a.ts - b.ts)) {
    if (r.date !== today || (r.deck || 'problems') !== deck) continue
    last.delete(r.id)                                // 先删再插, 顺序跟着最后一次走
    last.set(r.id, r.rating)
  }
  return [...last].filter(([, r]) => r === 1).map(([id]) => id)
}

/** 批注事件 -> card-comments.jsonl 的行(落回去之后 cid 就是 eid) */
export const commentRow = (ev: InboxEvent) => ({
  cid: ev.eid, ts: ev.ts, date: ev.date, deck: ev.deck, id: ev.id,
  title: ev.title || '', text: ev.text || '', status: 'open', pending: true,
})
