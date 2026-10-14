import { describe, expect, it } from 'vitest'
import { buildQuiz, cxPool, cxText } from '../quiz'

describe('buildQuiz', () => {
  it('单选: 正确项在选项里, 至多 4 项', () => {
    const q = buildQuiz({ quiz: { idea: 'A', wrong: ['B', 'C', 'D', 'E'] } })
    const st = q.ideas[0].state!
    expect(st.opts).toHaveLength(4)
    expect(st.opts).not.toContain('E')
    expect(st.opts[st.correct[0]]).toBe('A')
    expect(st.multi).toBe(false)
    expect(q.ideas[0].label).toBe('思路是哪个？')
  })
  it('idea 是数组 = 多选, 题干加「（多选）」', () => {
    const q = buildQuiz({ quiz: { idea: ['A', 'B'], wrong: ['C', 'D', 'E'] } })
    const st = q.ideas[0].state!
    expect(st.multi).toBe(true)
    expect(st.correct.map((i) => st.opts[i]).sort()).toEqual(['A', 'B'])
    expect(q.ideas[0].label).toBe('思路是哪个？（多选）')
  })
  it('then 接着问, 没写 idea 的步骤跳过; 第一问总在', () => {
    const q = buildQuiz({ quiz: { q: 'DFS 还是 BFS', then: [{ q: '哈希表?', idea: 'x', wrong: ['y'] }, { q: '空' }] } })
    expect(q.ideas.map((b) => b.label)).toEqual(['DFS 还是 BFS', '哈希表?'])
    expect(q.ideas[0].state).toBeNull()
  })
  it('复杂度那道默认关掉', () => {
    expect(buildQuiz({ quiz: {}, complexity: { time: 'O(n)', space: 'O(1)' } }).cx).toBeNull()
  })
})

describe('复杂度干扰项', () => {
  it('cxText', () => {
    expect(cxText({ time: 'O(n)' })).toBe('O(n) / ?')
    expect(cxText(null)).toBe('')
  })
  it('按出现频次抽, 排除正确项', () => {
    const ps = [
      { complexity: { time: 'O(n)', space: 'O(1)' } },
      { complexity: { time: 'O(n)', space: 'O(1)' } },
      { complexity: { time: 'O(n log n)', space: 'O(1)' } },
      { complexity: { time: 'O(1)', space: 'O(1)' } },
    ]
    expect(cxPool(ps, 'O(1) / O(1)')).toEqual(['O(n) / O(1)', 'O(n log n) / O(1)'])
  })
})
