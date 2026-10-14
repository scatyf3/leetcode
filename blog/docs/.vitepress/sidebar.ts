import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import matter from 'gray-matter'
import type { DefaultTheme } from 'vitepress'
import { layers } from './layers'

const docsRoot = fileURLToPath(new URL('..', import.meta.url))

/** 一层一组，组内按 frontmatter 的 order 排；index.md 当组标题的链接。 */
export function buildSidebar(): DefaultTheme.Sidebar {
  return layers.map((l) => {
    const abs = path.join(docsRoot, l.dir)
    const items = fs
      .readdirSync(abs)
      .filter((f) => f.endsWith('.md') && f !== 'index.md')
      .map((f) => {
        const fm = matter(fs.readFileSync(path.join(abs, f), 'utf8')).data
        const slug = f.replace(/\.md$/, '')
        return { text: fm.title ?? slug, link: `/${l.dir}/${slug}`, order: fm.order ?? 99, todo: fm.status === 'todo' }
      })
      .sort((a, b) => a.order - b.order || a.link.localeCompare(b.link))
      .map(({ text, link, todo }) => ({ text: todo ? `${text} ·` : text, link }))
    return { text: `L${l.id} ${l.name}`, link: `/${l.dir}/`, collapsed: false, items }
  })
}
