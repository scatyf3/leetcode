import { describe, expect, it } from 'vitest'
import { orderQueue, queuePool } from '../queue'

const T = '2026-10-01'
const probs = [
  { id: 5, status: 'solved', due: '2026-09-30', familiarity: 2 },          // 逾期
  { id: 3, status: 'review', due: '2026-10-01', familiarity: 1 },          // 今天到期, review 优先
  { id: 9, status: 'solved', due: '2026-10-05', familiarity: 4 },          // 没到期 -> 不进
  { id: 7, status: 'solved', familiarity: 1 },                             // 新卡, 较熟
  { id: 8, status: 'solved', familiarity: 4 },                             // 新卡, 生 -> 先
  { id: 6, status: 'solved' },                                              // 新卡, 未评
  { id: 2, status: 'todo', familiarity: 4 },                                // todo 不进
  { id: 4, status: 'solved', familiarity: 4, paused: '2026-09-01' },        // 暂停不进
]

describe('queuePool', () => {
  it('到期的卡 + 够格的新题, 暂停/todo/没到期的不进', () => {
    expect(queuePool(probs, 'problems', T).map((p) => p.id).sort((a, b) => a - b)).toEqual([3, 5, 6, 7, 8])
  })
  it('语法卡没有 status 这一层', () => {
    const cards = [{ id: 'a/x' }, { id: 'a/y', due: '2026-12-01' }, { id: 'a/z', due: '2026-09-01' }]
    expect(queuePool(cards, 'syntax', T).map((c) => c.id)).toEqual(['a/z', 'a/x'])
  })
})

describe('orderQueue', () => {
  const pool = queuePool(probs, 'problems', T)
  it('fsrs: review 优先 -> 到期日 -> 新卡按从生到熟', () => {
    expect(orderQueue(pool, 'fsrs', 'problems', T)).toEqual([3, 5, 8, 6, 7])
  })
  it('order: 题号升序', () => {
    expect(orderQueue(pool, 'order', 'problems', T)).toEqual([3, 5, 6, 7, 8])
  })
  it('random: 范围不变, 只换顺序', () => {
    expect([...orderQueue(pool, 'random', 'problems', T)].sort()).toEqual([3, 5, 6, 7, 8])
  })
  it('语法卡按书写顺序 ord, 不拿字符串 id 相减', () => {
    const cards = [{ id: 'b', ord: 2 }, { id: 'a', ord: 1 }, { id: 'c', ord: 0 }]
    expect(orderQueue(cards, 'order', 'syntax', T)).toEqual(['c', 'a', 'b'])
    expect(orderQueue(cards, 'fsrs', 'syntax', T)).toEqual(['c', 'a', 'b'])
  })
})
