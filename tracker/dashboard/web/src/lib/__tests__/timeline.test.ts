import { describe, expect, it } from 'vitest'
import { TL_GONE, buildTimeline, depthKey } from '../timeline'
import { famKey } from '../fam'

const famK = (s: { fam: number | null; exists: boolean }) => (s.exists ? famKey(s.fam) : TL_GONE)

describe('buildTimeline', () => {
  it('没有事件就没有时间轴', () => {
    expect(buildTimeline({ problems: [], edits: [], keyOf: famK, today: '2026-10-01' })).toBeNull()
  })

  it('从现状倒推, 再逐日正推; 最后一天等于现状', () => {
    const tl = buildTimeline({
      planGroups: [{ problems: [[1], [2], [3]] }],
      problems: [{ id: 1, familiarity: 2 }, { id: 2, familiarity: 4 }],
      edits: [
        { id: 2, field: 'exists', from: false, to: true, date: '2026-09-29', ts: 1 },
        { id: 1, field: 'familiarity', from: 4, to: 2, date: '2026-09-30', ts: 2 },
      ],
      keyOf: famK,
      today: '2026-10-01',
    })!
    expect(tl.total).toBe(3)
    expect(tl.days.map((d) => d.date)).toEqual(['2026-09-28', '2026-09-29', '2026-09-30', '2026-10-01'])
    expect(tl.days[0].c).toEqual({ 4: 1, [TL_GONE]: 2 })            // 1 是 L4, 2/3 还没建
    expect(tl.days[1].c).toEqual({ 4: 2, [TL_GONE]: 1 })            // 2 建了
    expect(tl.days[3].c).toEqual({ 2: 1, 4: 1, [TL_GONE]: 1 })      // = 现状
  })

  it('ids 只限制计数, 不限制回放; 窗口外的事件快进掉', () => {
    const tl = buildTimeline({
      problems: [{ id: 1, familiarity: 0 }, { id: 2, familiarity: 1 }],
      edits: [
        { id: 1, field: 'familiarity', from: null, to: 3, date: '2026-01-01', ts: 1 },
        { id: 1, field: 'familiarity', from: 3, to: 0, date: '2026-09-30', ts: 2 },
      ],
      keyOf: depthKey,
      ids: new Set([1]),
      today: '2026-10-01',
      maxDays: 3,
    })!
    expect(tl.total).toBe(1)
    expect(tl.days.map((d) => d.date)).toEqual(['2026-09-29', '2026-09-30', '2026-10-01'])
    expect(tl.days[0].c).toEqual({ 1: 1 })   // 快进过 1 月那条: L3 -> S1
    expect(tl.days[2].c).toEqual({ 3: 1 })   // L0 -> S3
  })
})
