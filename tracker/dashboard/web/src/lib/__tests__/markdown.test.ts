import { describe, expect, it } from 'vitest'
import { linkifyPids, renderMd, type PidIndex } from '../markdown'

const rec: PidIndex = new Map([
  [26, { id: 26, title: 'Remove Duplicates' }],
  [27, { id: 27, title: 'Remove Element' }],
  [42, { id: 42, title: 'Trapping Rain Water' }],
])
const links = (html: string) => [...html.matchAll(/data-pid="(\d+)"/g)].map((m) => +m[1])

describe('linkifyPids', () => {
  it('只认显式标记 LC / #', () => {
    expect(links(linkifyPids('见 LC 42。裸的 42 不算', rec))).toEqual([42])
    expect(links(linkifyPids('LC 26 和 27', rec))).toEqual([26, 27])   // 和 / 与 是连号
    expect(links(linkifyPids('#42', rec))).toEqual([42])
  })
  it('一串连号共用一个标记, 库里没有的留纯文本', () => {
    expect(links(linkifyPids('LC 26, 27、76', rec))).toEqual([26, 27])
  })
  it('"LC 1-1.5 小时" 里的数字不是题号', () => {
    expect(links(linkifyPids('每天 LC 1-1.5 小时', new Map([[1, { id: 1, title: 'Two Sum' }]])))).toEqual([])
  })
  it('不碰 code / 已有链接 / 标签属性', () => {
    const html = '<code>LC 42</code> <a href="x">LC 42</a> <span title="#42">x</span>'
    expect(linkifyPids(html, rec)).toBe(html)
  })
  it('空索引原样返回', () => expect(linkifyPids('LC 42', new Map())).toBe('LC 42'))
})

describe('renderMd', () => {
  it('嵌套列表不被拍平(换 marked 的原因)', () => {
    const html = renderMd('- a\n  - b\n    - c', rec)
    expect((html.match(/<ul>/g) || []).length).toBe(3)
  })
  it('链接新标签打开 + 题号链接', () => {
    const html = renderMd('[doc](../x.md) 参见 LC 42', rec)
    expect(html).toContain('<a target="_blank" href="../x.md">')
    expect(links(html)).toEqual([42])
  })
})
