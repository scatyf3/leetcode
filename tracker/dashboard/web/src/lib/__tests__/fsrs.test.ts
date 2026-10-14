import { describe, expect, it } from 'vitest'
import { addDays, daysBetween, newCard, preview, review, roundHalfEven, type Card, type Rating } from '../fsrs'
// dashboard/fsrs.py 跑出来的 60 条随机复习序列(同一天重评 / 提前 / 按时 / 逾期都有)。
// 改了 fsrs.py 就重新生成: python dashboard/fsrs.py --fixture dashboard/web/src/lib/__tests__/fixtures/fsrs-py.json
import cases from './fixtures/fsrs-py.json'

type Step = { rating: Rating; today: string; card: Card; interval: number; preview: Record<string, number> }

describe('fsrs.ts 和 fsrs.py 对拍', () => {
  it('每一步的间隔 / due / 预览都一致, S 和 D 只差浮点尾数', () => {
    let n = 0
    for (const steps of cases as Step[][]) {
      let c: Card = newCard()
      for (const s of steps) {
        const { card, interval } = review(c, s.rating, s.today)
        expect(interval).toBe(s.interval)
        expect(card.due).toBe(s.card.due)
        expect(card.reps).toBe(s.card.reps)
        expect(card.lapses).toBe(s.card.lapses)
        expect(card.stability).toBeCloseTo(s.card.stability!, 9)
        expect(card.difficulty).toBeCloseTo(s.card.difficulty!, 9)
        expect(preview(card, s.today)).toEqual({ 1: s.preview['1'], 2: s.preview['2'], 3: s.preview['3'], 4: s.preview['4'] })
        // 接着用 Python 那份算下一步, 浮点误差不会一路累积
        c = s.card
        n++
      }
    }
    expect(n).toBeGreaterThan(200)
  })

  it('不改传进来的卡', () => {
    const c = newCard()
    review(c, 3, '2026-01-01')
    expect(c).toEqual(newCard())
  })

  it('round 跟 Python 一样五成双', () => {
    expect([0.5, 1.5, 2.5, 2.6, 3.4].map(roundHalfEven)).toEqual([0, 2, 2, 3, 3])
  })

  it('日期按天算, 跨月跨年', () => {
    expect(addDays('2026-12-30', 3)).toBe('2027-01-02')
    expect(daysBetween('2026-02-27', '2026-03-02')).toBe(3)
  })
})
