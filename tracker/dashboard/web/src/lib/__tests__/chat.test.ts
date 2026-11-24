import { describe, expect, it } from 'vitest'
import { parseChat } from '../chat'

describe('parseChat', () => {
  it('splits sessions and speakers, keeps bot markdown headings inside the bubble', () => {
    const src = [
      '<!-- chat aaaa/1111 2026-11-20 -->', '', '#### 🧑 我', '', 'hint?', '',
      '#### 🤖 Claude', '', '## 提示 1', '', 'BFS', '', '---', '',
      '<!-- chat bbbb/2222 2026-11-22 -->', '', '#### 🧑 我', '', 'again', '',
      '#### 🤖 Claude', '', 'ok', '',
    ].join('\n')
    const s = parseChat(src)
    expect(s.map((x) => x.date)).toEqual(['2026-11-20', '2026-11-22'])
    expect(s[0].bubbles).toEqual([
      { who: 'me', text: 'hint?' },
      { who: 'bot', text: '## 提示 1\n\nBFS' },
    ])
    expect(s[1].bubbles[1]).toEqual({ who: 'bot', text: 'ok' })
  })

  it('treats hand-pasted text without markers as a single note', () => {
    expect(parseChat('随手粘的记录\n\n第二段')).toEqual([
      { key: '', date: '', bubbles: [{ who: 'note', text: '随手粘的记录\n\n第二段' }] },
    ])
  })

  it('keeps a hand-written preamble before the first session', () => {
    const s = parseChat('前言\n\n<!-- chat a/b 2026-01-01 -->\n\n#### 🧑 我\n\nq\n')
    expect(s).toHaveLength(2)
    expect(s[0].bubbles[0].who).toBe('note')
    expect(s[1].bubbles).toEqual([{ who: 'me', text: 'q' }])
  })
})
