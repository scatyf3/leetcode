import { createContentLoader } from 'vitepress'
import { layerByDir } from '../layers'

export type Status = 'todo' | 'draft' | 'reviewed'
export const STATUSES: Status[] = ['todo', 'draft', 'reviewed']

export interface Topic {
  url: string
  dir: string
  slug: string
  title: string
  status: Status
  order: number
  /** 绝对路径（不含 base），如 /structures/heap —— 跨层引用，首页图上画连线 */
  related: string[]
  /** 除 slug 以外，还有哪些 meta.json 标签算这一页的题 */
  alias: string[]
}

declare const data: Topic[]
export { data }

export default createContentLoader('*/*.md', {
  transform(raw): Topic[] {
    return raw
      .map((p) => {
        const [dir, slug = 'index'] = p.url.split('/').filter(Boolean)
        const fm = p.frontmatter
        if (!layerByDir[dir]) throw new Error(`[topics] ${p.url} 不在 layers.ts 的任何一层里`)
        if (!fm.title) throw new Error(`[topics] missing title in ${p.url}`)
        const status: Status = fm.status ?? 'todo'
        if (!STATUSES.includes(status)) {
          throw new Error(`[topics] invalid status "${status}" in ${p.url} (expected ${STATUSES.join(' | ')})`)
        }
        return {
          url: p.url,
          dir,
          slug,
          title: fm.title,
          status,
          order: fm.order ?? 99,
          related: fm.related ?? [],
          alias: fm.alias ?? [],
        }
      })
      .filter((t) => t.slug !== 'index')
      .sort((a, b) => a.order - b.order || a.slug.localeCompare(b.slug))
  },
})
