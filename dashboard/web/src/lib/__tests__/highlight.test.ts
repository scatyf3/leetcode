import { describe, expect, it } from 'vitest'
import { highlightPython } from '../highlight'

describe('highlightPython', () => {
  it('关键字 / 函数名 / 内建 / 数字', () => {
    const h = highlightPython('def f(n):\n    return len(n) + 1')
    expect(h).toContain('<span class="t-kw">def</span>')
    expect(h).toContain('<span class="t-fn">f</span>')
    expect(h).toContain('<span class="t-bi">len</span>')
    expect(h).toContain('<span class="t-num">1</span>')
  })
  it('注释和字符串里的 HTML 被转义', () => {
    const h = highlightPython('x = "<b>"  # a < b')
    expect(h).toContain('<span class="t-str">&quot;&lt;b&gt;&quot;</span>')
    expect(h).toContain('<span class="t-com"># a &lt; b</span>')
  })
  it('三引号字符串整段算一个 token', () => {
    const h = highlightPython('"""doc\nstring"""\nx')
    expect(h).toContain('<span class="t-str">&quot;&quot;&quot;doc\nstring&quot;&quot;&quot;</span>')
  })
  it('去掉标签后和原文一致(不丢字符)', () => {
    const src = 'class A:\n    @staticmethod\n    def g(self, s=\'a\\\'b\'): pass  # 注释'
    const text = highlightPython(src).replace(/<[^>]+>/g, '')
      .replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
    expect(text).toBe(src)
  })
})
