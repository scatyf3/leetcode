import { describe, expect, it } from 'vitest'
import { FAM_LEVELS, L_NEXT, depthOf, famCls, famInfo, famKey, famOf, ledgerOf } from '../fam'

describe('famOf', () => {
  it('缺键 / null / 空串都是未评, 不是 0', () => {
    expect(famOf({})).toBeNull()
    expect(famOf({ familiarity: null })).toBeNull()
    expect(famOf({ familiarity: '' })).toBeNull()
  })
  it('0 是最熟的一档, 不能被当成未评', () => {
    expect(famOf({ familiarity: 0 })).toBe(0)
    expect(famOf({ familiarity: '0' })).toBe(0)
  })
  it('半档原样保留', () => {
    expect(famOf({ familiarity: 1.5 })).toBe(1.5)
    expect(famOf({ familiarity: '3.5' })).toBe(3.5)
  })
})

describe('famKey / famCls', () => {
  it('类名里的小数点换成下划线, 对象键不换', () => {
    expect(famKey(1.5)).toBe('1.5')
    expect(famCls(1.5)).toBe('f1_5')
    expect(famCls(null)).toBe('fnone')
  })
  it('每一档都有标签', () => {
    for (const f of FAM_LEVELS) expect(famInfo(f).short).toBeTruthy()
  })
})

describe('depthOf', () => {
  it.each([
    [0, 3], [1, 2], [1.5, 2], [2, 2], [2.5, 2], [3, 1], [3.5, 0], [4, 0], [null, 0],
  ])('L%s -> S%s', (f, s) => {
    expect(depthOf({ familiarity: f })).toBe(s)
  })
  it('没建文件夹 = 0', () => expect(depthOf(undefined)).toBe(0))
})

describe('L_NEXT', () => {
  it('从未评一路走到 L0 再回到未评, 每档恰好经过一次', () => {
    const seen: (number | null)[] = []
    let k = 'none'
    for (let i = 0; i < 9; i++) {
      const nx = L_NEXT[k]
      seen.push(nx)
      k = famKey(nx)
    }
    expect(seen).toEqual([4, 3.5, 3, 2.5, 2, 1.5, 1, 0, null])
  })
})

describe('ledgerOf', () => {
  it('四档互斥, 横着加起来等于题数', () => {
    const rows = [
      { id: 1, rec: { familiarity: 0 } },
      { id: 2, rec: { familiarity: 3 } },
      { id: 3, rec: {} },
      { id: 4 },
      { id: 5 },
    ]
    const t = ledgerOf(rows, new Set([5]))
    expect(t).toEqual({ n: 5, seen: 3, touched: 2, s2: 1, debt: 1, absent: 1, prem: 1 })
    expect(t.s2 + t.debt + (t.seen - t.touched) + t.absent + t.prem).toBe(t.n)
  })
})
