import { todayStr } from './dates'
import { FAM_ORDER, famKey, famOf } from './fam'
import type { Deck, QueueMode } from './types'

// ---- 🧠 FSRS 复习队列 ------------------------------------------------------
// 调度状态在各题 meta.json 的 fsrs 字段里, 算法在 dashboard/fsrs.py。
// 和 familiarity(L1-L4) 是**两套独立的东西**: 这里只管"什么时候再问一次"。

type Row = {
  id: number | string
  due?: string | null
  status?: string
  paused?: unknown
  familiarity?: unknown
  ord?: number
}

export const isCard = (p: Row) => !!p.due
export const isDue = (p: Row, today = todayStr()) => isCard(p) && (p.due as string) <= today
export const rvEligible = (p: Row) => p.status === 'solved' || p.status === 'review'

// 队列**范围**三种模式都一样(到期的卡 + 还没进过复习的题), 模式只决定**顺序**:
//   fsrs   到期优先 + 生的优先(默认)
//   order  题号升序
//   random 随机
export const RV_MODES: QueueMode[] = ['fsrs', 'order', 'random']

// problems 题目(真相在各题 meta.json) / syntax 语法卡(真相在 syntax/*.md)。
// 两边**只共用调度器和历史**, 排队规则各写各的 —— 语法卡没有 status 也没有 familiarity,
// 硬套题目那套会得到一个"全 undefined 参与排序"的随机顺序。
export const DECKS: Deck[] = ['problems', 'syntax']
export const DECK_LABEL: Record<Deck, string> = { problems: '题目', syntax: '语法' }

export const shuffle = <T>(a: T[]): T[] => {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// 队列范围: 到期的卡 + 还没进过复习的。题目那边"还没进过"要先够格(status 是 solved/review,
// 没想出来过的思路谈不上复习); 语法卡只要写在 syntax/*.md 里就算数, 没有这一层。
// 暂停的题整个不进队列(徽章也就不数它)。调度数据原样留着 —— 恢复时服务端把 due / last_review
// 一起往后推停掉的天数, 所以回来时不会是一大片逾期(见 server.set_paused)。
export function queuePool<T extends Row>(rows: T[], deck: Deck = 'problems', today = todayStr()): T[] {
  const live = rows.filter((p) => !p.paused)
  const fresh = deck === 'syntax' ? live : live.filter(rvEligible)
  return [...live.filter((p) => isDue(p, today)), ...fresh.filter((p) => !isCard(p))]
}

export function orderQueue<T extends Row>(
  pool: T[], mode: QueueMode = 'fsrs', deck: Deck = 'problems', today = todayStr(),
): T['id'][] {
  // 组内的稳定兜底顺序。题目按题号; 语法卡按 ord(= /api/syntax 的下标, 也就是
  // 文件名 -> 文件内的书写顺序)。**别拿 a.id - b.id 排语法卡** —— id 是字符串,
  // 相减得 NaN, 比较器全返回 NaN 等于没排序, 表现是顺序每次都不一样。
  const tie = deck === 'syntax'
    ? (a: T, b: T) => (a.ord || 0) - (b.ord || 0)
    : (a: T, b: T) => (a.id as number) - (b.id as number)
  if (mode === 'random') return shuffle(pool.map((p) => p.id))
  if (mode === 'order') return [...pool].sort(tie).map((p) => p.id)
  const due = pool.filter((p) => isDue(p, today)).sort((a, b) =>
    (a.status === 'review' ? 0 : 1) - (b.status === 'review' ? 0 : 1) ||
    (a.due as string).localeCompare(b.due as string) || tie(a, b))
  // 还没成为卡片的题, 按熟练度从生到熟排 —— 只是**读** familiarity 定顺序, 不写它。
  // 语法卡没有这个字段, 就按书写顺序来(同一个文件里相关的卡挨着问, 正好对照)。
  const fresh = pool.filter((p) => !isCard(p)).sort(deck === 'syntax' ? tie
    : (a, b) => FAM_ORDER[famKey(famOf(a))] - FAM_ORDER[famKey(famOf(b))] || tie(a, b))
  return [...due, ...fresh].map((p) => p.id)
}
