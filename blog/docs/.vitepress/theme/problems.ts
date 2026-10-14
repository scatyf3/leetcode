import type { Layer } from '../layers'
import type { Problem } from '../data/problems.data'
import type { Topic } from '../data/topics.data'

/** 这一页挂了哪些题：meta.json 里 layer.tag 那个字段含 slug 或 alias 之一。python 层没有 tag，恒为空。 */
export function problemsOf(all: Problem[], layer: Layer, t: Pick<Topic, 'slug' | 'alias'>): Problem[] {
  if (!layer.tag) return []
  const keys = new Set([t.slug, ...t.alias])
  return all.filter((p) => p[layer.tag!].some((k) => keys.has(k)))
}
