// FSRS-6 调度器的 TS 版 —— **逐行照抄 dashboard/fsrs.py**, 不是另找一份实现。
//
// 只给只读站用: 手机上评完分要立刻知道下次哪天到期、按钮上标几天。真正落盘的那一次
// 由本机 server.py 重放同一条事件、用 fsrs.py 再算一遍(见 dashboard/inbox.py),
// 所以这里算出来的只是临时显示 —— 但两边必须一致, 否则手机上说「8 天后」, 落回来变成 7 天。
// 单测里拿 fsrs.py 跑出来的数对拍(__tests__/fsrs.test.ts)。
//
// 没有 fsrs_params.json 的自定义参数: 那个文件不导出, 有了它两边就会对不上 ——
// 真要跑优化器换参数, 记得这里也读一份。

export const FSRS_DEFAULT_DECAY = 0.1542
export const DEFAULT_W = [
  0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001,
  1.8722, 0.1666, 0.796, 1.4835, 0.0614, 0.2629, 1.6483, 0.6014,
  1.8729, 0.5425, 0.0912, 0.0658,
  FSRS_DEFAULT_DECAY,
]
export const DEFAULT_RETENTION = 0.9
const MAXIMUM_INTERVAL = 36500
const STABILITY_MIN = 0.001
const MIN_DIFFICULTY = 1.0
const MAX_DIFFICULTY = 10.0

export type Rating = 1 | 2 | 3 | 4
export const RATINGS: Rating[] = [1, 2, 3, 4]

export interface Card {
  state?: string
  due?: string
  last_review?: string
  stability?: number
  difficulty?: number
  reps?: number
  lapses?: number
  last_rating?: number
}

const w = DEFAULT_W
const E = Math.E

const clampD = (d: number) => Math.min(Math.max(d, MIN_DIFFICULTY), MAX_DIFFICULTY)
const clampS = (s: number) => Math.max(s, STABILITY_MIN)

function decayFactor(): [number, number] {
  const decay = -(w.length > 20 ? w[20] : 0.5)
  return [decay, 0.9 ** (1 / decay) - 1]
}

const initialStability = (r: Rating) => clampS(w[r - 1])

function initialDifficulty(r: Rating, clamp = true) {
  const d = w[4] - E ** (w[5] * (r - 1)) + 1
  return clamp ? clampD(d) : d
}

const linearDamping = (delta: number, d: number) => ((10.0 - d) * delta) / 9.0
const meanReversion = (a1: number, a2: number) => w[7] * a1 + (1 - w[7]) * a2

function nextDifficulty(d: number, r: Rating) {
  const a1 = initialDifficulty(4, false)
  const delta = -(w[6] * (r - 3))
  return clampD(meanReversion(a1, d + linearDamping(delta, d)))
}

function shortTermStability(s: number, r: Rating) {
  let inc = E ** (w[17] * (r - 3 + w[18])) * s ** -w[19]
  if (r !== 1) inc = Math.max(inc, 1.0)
  return clampS(s * inc)
}

function nextForgetStability(d: number, s: number, ret: number) {
  const longTerm = w[11] * d ** -w[12] * ((s + 1) ** w[13] - 1) * E ** ((1 - ret) * w[14])
  const shortTerm = s / E ** (w[17] * w[18])
  return Math.min(longTerm, shortTerm)
}

function nextRecallStability(d: number, s: number, ret: number, r: Rating) {
  const hard = r === 2 ? w[15] : 1
  const easy = r === 4 ? w[16] : 1
  return s * (1 + E ** w[8] * (11 - d) * s ** -w[9] * (E ** ((1 - ret) * w[10]) - 1) * hard * easy)
}

const nextStability = (d: number, s: number, ret: number, r: Rating) =>
  clampS(r === 1 ? nextForgetStability(d, s, ret) : nextRecallStability(d, s, ret, r))

function retrievabilityOf(s: number, elapsed: number) {
  const [decay, factor] = decayFactor()
  if (!s) return 0.0
  return (1 + (factor * Math.max(0, elapsed)) / s) ** decay
}

/** Python 的 round() 是四舍六入五成双, Math.round 是 .5 往上 —— 照着 Python 来 */
export function roundHalfEven(x: number) {
  const f = Math.floor(x)
  const diff = x - f
  if (diff > 0.5) return f + 1
  if (diff < 0.5) return f
  return f % 2 === 0 ? f : f + 1
}

function nextInterval(s: number, retention: number) {
  const [decay, factor] = decayFactor()
  const n = roundHalfEven((s / factor) * (retention ** (1 / decay) - 1))
  return Math.max(1, Math.min(n, MAXIMUM_INTERVAL))
}

// ---- 日期: 'YYYY-MM-DD', 按 UTC 算天数, 不受时区 / 夏令时影响 ----
const dayNum = (s: string) => {
  const [y, m, d] = s.split('-').map(Number)
  return Date.UTC(y, m - 1, d) / 864e5
}
export const addDays = (s: string, n: number) => new Date((dayNum(s) + n) * 864e5).toISOString().slice(0, 10)
export const daysBetween = (a: string, b: string) => Math.round(dayNum(b) - dayNum(a))

export const newCard = (): Card => ({ state: 'new', reps: 0, lapses: 0 })

/** 评一次分, 返回新卡和间隔(天)。card 不会被就地修改。和 fsrs.review 一一对应 */
export function review(card: Card | null | undefined, rating: Rating, today: string): { card: Card; interval: number } {
  if (!RATINGS.includes(rating)) throw new Error(`rating 必须是 1..4, 收到 ${rating}`)
  const c = { ...(card || {}) }
  const last = c.last_review || ''
  const elapsed = last ? daysBetween(last, today) : null

  const isNew = (c.state ?? 'new') === 'new' || !c.stability
  let stability: number
  let difficulty: number
  if (isNew) {
    stability = initialStability(rating)
    difficulty = initialDifficulty(rating)
  } else {
    const s0 = Number(c.stability), d0 = Number(c.difficulty)
    if (elapsed !== null && elapsed < 1) {
      stability = shortTermStability(s0, rating)
    } else {
      stability = nextStability(d0, s0, retrievabilityOf(s0, elapsed || 0), rating)
    }
    difficulty = nextDifficulty(d0, rating)
  }
  const interval = nextInterval(stability, DEFAULT_RETENTION)
  return {
    card: {
      state: 'review',
      due: addDays(today, interval),
      last_review: today,
      stability,
      difficulty,
      reps: (c.reps || 0) + 1,
      lapses: (c.lapses || 0) + (rating === 1 && !isNew ? 1 : 0),
      last_rating: rating,
    },
    interval,
  }
}

/** 四个按钮各自排到几天后, 和 /api/problems/{id} 的 fsrs_preview 同形状 */
export function preview(card: Card | null | undefined, today: string): Record<Rating, number> {
  const out = {} as Record<Rating, number>
  for (const r of RATINGS) out[r] = review(card, r, today).interval
  return out
}
