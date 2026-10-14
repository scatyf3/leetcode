import { describe, expect, it } from 'vitest'
import { dAdd, daysSince, fmtDays, fmtInterval, mmdd, weekStart } from '../dates'

describe('dAdd', () => {
  it('跨月 / 跨年 / 闰日', () => {
    expect(dAdd('2026-01-31', 1)).toBe('2026-02-01')
    expect(dAdd('2025-12-31', 1)).toBe('2026-01-01')
    expect(dAdd('2028-02-28', 1)).toBe('2028-02-29')
    expect(dAdd('2026-03-01', -1)).toBe('2026-02-28')
  })
})

describe('weekStart', () => {
  it('一周从周一算', () => {
    expect(weekStart('2026-10-01')).toBe('2026-09-28') // 周四
    expect(weekStart('2026-09-28')).toBe('2026-09-28') // 周一本身
    expect(weekStart('2026-10-04')).toBe('2026-09-28') // 周日还算上一周
  })
})

describe('格式化', () => {
  it('mmdd', () => expect(mmdd('2026-10-01')).toBe('10/01'))
  it('fmtInterval: 0 是今天', () => {
    expect(fmtInterval(0)).toBe('今天')
    expect(fmtInterval(1)).toBe('明天')
    expect(fmtInterval(12)).toBe('12 天')
    expect(fmtInterval(45)).toBe('1.5 个月')
    expect(fmtInterval(730)).toBe('2.0 年')
  })
  it('fmtDays: 0 是没有, 不是今天', () => {
    expect(fmtDays(0)).toBe('—')
    expect(fmtDays(0.4)).toBe('<1 天')
    expect(fmtDays(3.25)).toBe('3.3 天')
    expect(fmtDays(14)).toBe('14 天')
  })
  it('daysSince', () => expect(daysSince('2026-09-24', '2026-10-01')).toBe(7))
})
