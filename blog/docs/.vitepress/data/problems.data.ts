import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// 构建时把 tracker/<题>/meta.json 扫一遍：页面底部「挂在这里的题」就从这儿来。
// 真相源还是 meta.json，这里只读。
const TRACKER = fileURLToPath(new URL('../../../../tracker', import.meta.url))
const GH = 'https://github.com/scatyf3/leetcode/tree/main/tracker/'

export interface Problem {
  id: number
  title: string
  url: string
  difficulty: string
  status: string
  /** 0 最熟 … 4 最生；null = 未评。阶梯见 tracker/dashboard/README.md */
  familiarity: number | null
  structures: string[]
  paradigms: string[]
}

declare const data: Problem[]
export { data }

export default {
  load(): Problem[] {
    const out: Problem[] = []
    for (const folder of fs.readdirSync(TRACKER)) {
      const m = /^(\d+)\.\s+(.+)$/.exec(folder)
      const f = path.join(TRACKER, folder, 'meta.json')
      if (!m || !fs.existsSync(f)) continue
      let meta: any
      try {
        meta = JSON.parse(fs.readFileSync(f, 'utf8'))
      } catch {
        continue
      }
      out.push({
        id: Number(m[1]),
        title: m[2],
        url: GH + encodeURIComponent(folder),
        difficulty: meta.difficulty ?? '',
        status: meta.status ?? 'todo',
        familiarity: typeof meta.familiarity === 'number' ? meta.familiarity : null,
        structures: meta.structures ?? [],
        paradigms: meta.paradigms ?? [],
      })
    }
    return out.sort((a, b) => a.id - b.id)
  },
}
