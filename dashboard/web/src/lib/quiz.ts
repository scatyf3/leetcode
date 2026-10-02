import { shuffle } from './queue'

type Complexity = { time?: string; space?: string } | null | undefined

export const cxText = (c: Complexity) => (c && c.time ? `${c.time} / ${c.space || '?'}` : '')

// 复杂度的干扰项从全库出现过的复杂度里抽, 并且**优先抽常见的** ——
// 抽到 O(n^(T/min)) 那种独一份的等于送分, 抽到 O(n)/O(n) 才是真的容易混。
export function cxPool(problems: { complexity?: Complexity }[], correct: string): string[] {
  const freq = new Map<string, number>()
  for (const p of problems) {
    const t = cxText(p.complexity)
    if (t && t !== correct) freq.set(t, (freq.get(t) || 0) + 1)
  }
  return [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).map((x) => x[0])
}

export interface QuizState { opts: string[]; correct: number[]; multi: boolean; pick: number[] }
export interface QuizBlock { key: string; label: string; state: QuizState | null }

interface QuizStep { q?: string; idea?: string | string[]; wrong?: string[]; then?: QuizStep[] }

// 复杂度那道先关掉: 思路还没稳的时候先问思路, 复杂度等思路熟了再开。
// 改成 true 就能把「时间/空间复杂度？」那道题恢复出来, 其余逻辑都还在。
export const QUIZ_CX = false

// quiz 可以拆成几步问: 顶层 {q?, idea, wrong} 是第一问, then: [{q, idea, wrong}, ...] 接着问。
// 比如 133 先问「DFS 还是 BFS」, 再问「哈希表怎么用」—— 一句话塞两个考点, 选对了也分不清是哪个会了。
// 第一问的块总是在(没写选项时模板显示提示), then 里没写 idea 的直接跳过。
// idea 写成数组就是**多选**: 几个都对、要全选中才算对。用在「两种说法其实是一回事」的题上
// (139: 图的可达性 = 一维 DP) —— 单选里放一个「两者都行」, 做多了会发现"都行"那项总是对的。
export function buildQuiz(
  d: { quiz?: QuizStep; complexity?: Complexity },
  problems: { complexity?: Complexity }[] = [],
  withCx = QUIZ_CX,
): { ideas: QuizBlock[]; cx: QuizState | null } {
  const q = d.quiz || {}
  const cx = cxText(d.complexity)
  const mk = (correct: string | string[] | undefined, wrongs: string[]): QuizState | null => {
    const rights = ([] as string[]).concat(correct || []).filter(Boolean)
    if (!rights.length || wrongs.length < 1) return null
    const opts = shuffle([...rights, ...wrongs.slice(0, 4 - rights.length)]) // 总共至多 4 项(ABCD)
    return { opts, correct: rights.map((t) => opts.indexOf(t)), multi: rights.length > 1, pick: [] }
  }
  const steps: QuizStep[] = [q, ...(Array.isArray(q.then) ? q.then : [])]
  return {
    ideas: steps
      .map((s, i) => {
        const state = s.idea ? mk(s.idea, s.wrong || []) : null
        const label = s.q || (i ? '然后呢？' : '思路是哪个？')
        return { key: `idea${i}`, label: state && state.multi ? `${label}（多选）` : label, state }
      })
      .filter((b, i) => i === 0 || b.state),
    cx: withCx && cx ? mk(cx, shuffle(cxPool(problems, cx)).slice(0, 3)) : null,
  }
}
