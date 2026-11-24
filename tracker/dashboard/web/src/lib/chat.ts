// chat.md(dashboard/save_chat.py 导出的 Claude Code 讨论记录)-> 按会话分段、按说话人分气泡。
//   <!-- chat 6f2a01ea/1a2b3c4d 2026-11-22 -->   一段会话
//   #### 🧑 我 / #### 🤖 Claude                   说话人
// 第一个会话标记之前的内容(手粘的 claude.ai 记录之类)单独成段, 没有说话人行就整段当一个 note 气泡。

export type Bubble = { who: 'me' | 'bot' | 'note'; text: string }
export type ChatSession = { key: string; date: string; bubbles: Bubble[] }

const MARK = /^<!-- chat (\S+) (\S+) -->$/gm
const WHO = /^#### (🧑|🤖) .*$/gm

function bubbles(src: string): Bubble[] {
  const out: Bubble[] = []
  const parts = src.split(WHO)                 // [前言, 符号, 正文, 符号, 正文, ...]
  const pre = parts[0].replace(/\n-{3,}\s*$/, '').trim()
  if (pre) out.push({ who: 'note', text: pre })
  for (let i = 1; i < parts.length; i += 2) {
    // 段与段之间 save_chat 用 --- 隔开, 别把它渲染成最后一个气泡里的横线
    const text = parts[i + 1].replace(/\n-{3,}\s*$/, '').trim()
    if (text) out.push({ who: parts[i] === '🧑' ? 'me' : 'bot', text })
  }
  return out
}

export function parseChat(src: string): ChatSession[] {
  const marks = [...src.matchAll(MARK)]
  const out: ChatSession[] = []
  const head = src.slice(0, marks.length ? marks[0].index : src.length)
  if (head.trim()) out.push({ key: '', date: '', bubbles: bubbles(head) })
  marks.forEach((m, i) => {
    const end = i + 1 < marks.length ? marks[i + 1].index : src.length
    const b = bubbles(src.slice(m.index! + m[0].length, end))
    if (b.length) out.push({ key: m[1], date: m[2], bubbles: b })
  })
  return out
}
