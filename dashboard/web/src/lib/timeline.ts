import { dAdd, todayStr } from './dates'
import { depthOf, famOf } from './fam'
import type { Edit, Familiarity } from './types'

// ---- 掌握度时间轴: 每天各档各有几道题 ----------------------------------------
// **不落第二份统计**。最右边那一列直接来自 /api/problems, 是真相;
// 往左靠 edits.jsonl 里每条改动的 from 值一步步倒推, 再正推回来逐日取快照。
// 好处是"今天"永远和看板对得上 —— 日志漏记的手改(直接编辑 meta.json)只会让更早的
// 那几天偏一点, 不会让整条线整体漂掉。
//
// 分母是**题单 ∪ 仓库**: 没建文件夹的题也得占一格, 否则"未做"这一层就画不出来,
// 曲线会变成"总量凭空长大", 而不是"未做在被吃掉"。

export const TL_MAX_DAYS = 120 // 一列一天, 再长就挤不下了, 只画最近这些天
export const TL_GONE = 'gone' // 还没建文件夹 = 未做

export interface TlState { fam: Familiarity; exists: boolean }

/** 按算出来的深度归档 —— 配速图固定按 S 读 */
export const depthKey = (s: TlState) => (!s.exists ? TL_GONE : String(depthOf({ familiarity: s.fam })))

export interface TimelineInput {
  /** plan.json 的 groups: 每组 problems 是 [id, title, diff] */
  planGroups?: { problems: [number, ...unknown[]][] }[]
  problems: { id: number; familiarity?: unknown }[]
  edits: Edit[] | null
  /** 怎么把一道题的状态归档 */
  keyOf: (s: TlState) => string
  /** 只**统计**这些题(其余照样跟着回放状态, 只是不计数) —— 配速图要的是某一层 */
  ids?: Set<number> | null
  today?: string
  maxDays?: number
}

export interface Timeline { days: { date: string; c: Record<string, number> }[]; total: number }

export function buildTimeline(o: TimelineInput): Timeline | null {
  const only = o.ids || null
  const today = o.today || todayStr()
  const st = new Map<number, TlState>() // id -> {fam, exists}, 先铺现状
  for (const g of o.planGroups || []) for (const p of g.problems) st.set(p[0], { fam: null, exists: false })
  for (const p of o.problems) st.set(p.id, { fam: famOf(p), exists: true })

  const evs = (o.edits || [])
    .filter((e) => e.date && st.has(e.id) && (e.field === 'familiarity' || e.field === 'exists'))
    .sort((a, b) => (a.ts || 0) - (b.ts || 0))
  if (!evs.length) return null

  const set = (e: Edit, v: unknown) => {
    const s = st.get(e.id)!
    if (e.field === 'exists') s.exists = !!v
    else s.fam = v === null || v === undefined || v === '' ? null : Number(v)
  }
  for (let i = evs.length - 1; i >= 0; i--) set(evs[i], evs[i].from) // 倒推到第一条事件之前

  const floor = dAdd(today, -((o.maxDays ?? TL_MAX_DAYS) - 1))
  let start = dAdd(evs[0].date as string, -1) // 多留一列: 什么都还没发生的样子
  let i = 0
  if (start < floor) { // 太久远的那段直接快进掉, 只留最近的窗口
    start = floor
    while (i < evs.length && (evs[i].date as string) < start) { set(evs[i], evs[i].to); i++ }
  }
  const days: Timeline['days'] = []
  for (let d = start; d <= today; d = dAdd(d, 1)) {
    while (i < evs.length && (evs[i].date as string) <= d) { set(evs[i], evs[i].to); i++ }
    const c: Record<string, number> = {}
    for (const [id, s] of st) {
      if (only && !only.has(id)) continue
      const k = o.keyOf(s)
      c[k] = (c[k] || 0) + 1
    }
    days.push({ date: d, c })
  }
  // 日志里全是未来日期(手改过时间戳之类)的话一天都取不到, 别让下面拿 days[-1]
  return days.length ? { days, total: only ? only.size : st.size } : null
}
