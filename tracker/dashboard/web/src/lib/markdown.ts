import { Marked, type TokenizerAndRendererExtension } from 'marked'
import katex from 'katex'
import { esc } from './esc'

// ---- 题号 -> 可点链接 ------------------------------------------------------
// 只认**显式标记**: "LC 42"、"LC42"、"#42"。一串连号共用一个标记 ——
// "LC 26, 27"、"LC 5/647"、"LC 3、76、209、424" 里每个数字都会各自去查,
// 库里没有的(76/209 这种还没做的)保持纯文本, 不生成死链。
//
// 为什么不猜裸数字: 试过一版启发式(值域/量词/左右边界一堆规则), 全库能跑对,
// 但规则不可预测 —— 写文档的时候没法一眼知道 "各 1 个标量" 的 1 会不会变成链接。
// 显式标记的代价只是多打三个字符, 换来的是渲染结果完全可预期。
//
// 只碰纯文本: <code> 里的 2i+1、<a href="../paradigms/1d-dp.md"> 里的路径、
// 标签属性里的数字都不能动, 所以先按「标签/代码/已有链接」切段, 只改偶数段。
const PID_SEG = /(<code[\s\S]*?<\/code>|<a\b[\s\S]*?<\/a>|<[^>]*>)/
// 标记 + 一串用 / , 、 和 与 连起来的题号
// 末尾的否定环视: "每天 LC 1-1.5 小时" 里 LC 是网站名, 1 是时长不是题号
const PID_RUN = /(?:LC\s*|#)\d{1,4}(?:\s*(?:[\/,、]|和|与)\s*\d{1,4})*(?![\w.%\-–—])/gi
const PID_ONE = /\d{1,4}/g

export type PidIndex = Map<number, { id: number; title: string }>

export function linkifyPids(html: string, rec: PidIndex): string {
  if (!rec.size) return html
  return html.split(PID_SEG).map((seg, k) => {
    if (k % 2) return seg                        // 捕获组 = 标签/代码/已有链接, 原样放回
    return seg.replace(PID_RUN, (run) =>
      run.replace(PID_ONE, (num) => {
        const p = rec.get(+num)
        return p
          ? `<a class="pid" data-pid="${p.id}" title="${esc(p.id + '. ' + p.title)}">${num}</a>`
          : num                                  // 还没做的题: 留字, 不留链
      }))
  }).join('')
}

// ---- 公式: $...$ 行内, $$...$$ 独立成块 -------------------------------------
// 跟 GitHub 同一套写法, 仓库里的 note.md 在两边长一个样。
//
// 为什么先留占位、最后才换成 KaTeX: KaTeX 吐出来的是一层套一层的 <span>, 里面的文字
// (比如 \text{LC 42}) 会被 linkifyPids 当成题号。它只会按单个标签切段, 跳不过嵌套,
// 所以公式先渲成一个空的 <span data-math="i">, 等题号链接做完再换回去。
const MATH_SLOT = /<span data-math="(\d+)"><\/span>/g
let slots: string[] = []

function slot(tex: string, display: boolean): string {
  slots.push(katex.renderToString(tex, { displayMode: display, throwOnError: false }))
  return `<span data-math="${slots.length - 1}"></span>`
}

// 行内 $x$ 的边界跟 pandoc 一致: 开头 $ 后面、结尾 $ 前面都不能是空格, 结尾 $ 后面不能
// 紧跟数字 —— 这样 "$5 和 $10" 这种钱数不会被当成公式。要写字面的 $ 用 \$。
const INLINE = /^\$\$([\s\S]+?)\$\$|^\$(?!\s)([^\n$]+?)(?<!\s)\$(?!\d)/
const BLOCK = /^ {0,3}\$\$([\s\S]+?)\$\$[^\S\n]*(?:\n|$)/

const math: TokenizerAndRendererExtension[] = [
  {
    name: 'mathBlock',
    level: 'block',
    start: (src) => src.match(/^ {0,3}\$\$/m)?.index,
    tokenizer(src) {
      const m = BLOCK.exec(src)
      if (m) return { type: 'mathBlock', raw: m[0], text: m[1].trim() }
    },
    renderer: (t) => `<p class="math-block">${slot(t.text, true)}</p>\n`,
  },
  {
    name: 'mathInline',
    level: 'inline',
    start: (src) => {
      const i = src.indexOf('$')
      return i < 0 ? undefined : i
    },
    tokenizer(src) {
      const m = INLINE.exec(src)
      if (m) return { type: 'mathInline', raw: m[0], text: (m[1] ?? m[2]).trim(), display: m[1] !== undefined }
    },
    renderer: (t) => slot(t.text, t.display),
  },
]

// ---- markdown 渲染: marked + 三层后处理 ------------------------------------
// marked 锁在 15.0.7, 和原先 vendor 进仓库的那份同一个版本 —— 渲染结果不变。
const md = new Marked({ gfm: true, breaks: false, async: false, extensions: math })

export function renderMd(src: unknown, rec: PidIndex): string {
  slots = []
  const html = md.parse(String(src)) as string
  // 1) 文档里的链接指向仓库文件, 一律新标签打开
  // 2) 题号 -> 可点链接。它的跳过依据正是上面生成的 <code>/<a>
  // 3) 公式占位换回 KaTeX, 必须在 2) 之后
  const linked = linkifyPids(html.replace(/<a href=/g, '<a target="_blank" href='), rec)
  return linked.replace(MATH_SLOT, (_, i) => slots[+i])
}
