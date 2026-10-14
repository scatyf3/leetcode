/**
 * 套路的子集：frontmatter 写 `parent: <同层 slug>`，这一页就挂到那一页下面（如 滑动窗口 ⊂ 双指针）。
 * 只许一层 —— 父页自己不能再有 parent。sidebar（node 侧，gray-matter 读）和主题组件（topics.data）共用这一份。
 */
export interface Nestable {
  slug: string
  parent?: string
}

export type Nested<T> = T & { children: T[] }

/** 输入已按 order 排好；输出只剩顶层，子页按原顺序挂进 children。parent 写错直接抛错让构建失败。 */
export function nest<T extends Nestable>(items: T[], where: string): Nested<T>[] {
  const bySlug = new Map(items.map((t) => [t.slug, t]))
  for (const t of items) {
    if (!t.parent) continue
    const p = bySlug.get(t.parent)
    if (!p) throw new Error(`[nest] ${where}/${t.slug}: parent "${t.parent}" 不是同层的页面`)
    if (p.slug === t.slug) throw new Error(`[nest] ${where}/${t.slug}: parent 不能是自己`)
    if (p.parent) throw new Error(`[nest] ${where}/${t.slug}: parent "${p.slug}" 自己也有 parent，只许一层`)
  }
  return items
    .filter((t) => !t.parent)
    .map((t) => ({ ...t, children: items.filter((c) => c.parent === t.slug) }))
}
