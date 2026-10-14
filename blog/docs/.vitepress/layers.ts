/**
 * 三层：底下是 Python 给的现成容器，中间是概念上的数据结构，最上面是算法套路。
 * 一层 = docs/ 下的一个目录。这是唯一手工维护的结构信息，sidebar 和首页分层图都从这里 + frontmatter 生成。
 *
 * tag：这一层的页面和 tracker/<题>/meta.json 里哪个字段对得上 —— 页面 slug（或 frontmatter 的 alias）
 * 等于 meta.json 那个字段里的某个标签，题就会列在页面底部。python 层没有对应字段，不列题。
 */
export interface Layer {
  id: number
  dir: string
  name: string
  en: string
  scope: string
  color: string
  tag?: 'structures' | 'paradigms'
}

export const layers: Layer[] = [
  {
    id: 1, dir: 'python', name: 'Python 内置', en: 'Built-ins', color: '#0ea5e9',
    scope: '这个 API 底下是什么，复杂度从哪来',
  },
  {
    id: 2, dir: 'structures', name: '概念数据结构', en: 'Data Structures', color: '#22c55e', tag: 'structures',
    scope: '每多维护一种信息，就多一种结构',
  },
  {
    id: 3, dir: 'paradigms', name: '算法套路', en: 'Paradigms', color: '#f97316', tag: 'paradigms',
    scope: '题型 → 模板 → 坑',
  },
]

export const layerByDir = Object.fromEntries(layers.map((l) => [l.dir, l])) as Record<string, Layer>
