import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import matter from 'gray-matter'
import type { DefaultTheme } from 'vitepress'
import { layers } from './layers'
import { nest } from './nest'

const docsRoot = fileURLToPath(new URL('..', import.meta.url))

/** 一层一组，组内按 frontmatter 的 order 排；index.md 当组标题的链接。有 parent 的页缩进挂在父页下面。 */
export function buildSidebar(): DefaultTheme.Sidebar {
  return layers.map((l) => {
    const abs = path.join(docsRoot, l.dir)
    const items = fs
      .readdirSync(abs)
      .filter((f) => f.endsWith('.md') && f !== 'index.md')
      .map((f) => {
        const fm = matter(fs.readFileSync(path.join(abs, f), 'utf8')).data
        const slug = f.replace(/\.md$/, '')
        return {
          slug, parent: fm.parent as string | undefined,
          text: fm.title ?? slug, link: `/${l.dir}/${slug}`, order: fm.order ?? 99, todo: fm.status === 'todo',
        }
      })
      .sort((a, b) => a.order - b.order || a.link.localeCompare(b.link))
    const item = ({ text, link, todo }: (typeof items)[number]): DefaultTheme.SidebarItem =>
      ({ text: todo ? `${text} ·` : text, link })
    return {
      text: `L${l.id} ${l.name}`, link: `/${l.dir}/`, collapsed: false,
      items: nest(items, l.dir).map((t) =>
        t.children.length ? { ...item(t), collapsed: false, items: t.children.map(item) } : item(t)),
    }
  })
}
