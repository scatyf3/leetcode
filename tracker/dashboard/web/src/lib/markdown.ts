import { marked } from 'marked'
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

// ---- markdown 渲染: marked + 两层后处理 ------------------------------------
// marked 锁在 15.0.7, 和原先 vendor 进仓库的那份同一个版本 —— 渲染结果不变。
const MD_OPT = { gfm: true, breaks: false, async: false } as const

export function renderMd(src: unknown, rec: PidIndex): string {
  const html = marked.parse(String(src), MD_OPT) as string
  // 1) 文档里的链接指向仓库文件, 一律新标签打开
  // 2) 题号 -> 可点链接。放在最后, 因为它的跳过依据正是上面生成的 <code>/<a>
  return linkifyPids(html.replace(/<a href=/g, '<a target="_blank" href='), rec)
}
