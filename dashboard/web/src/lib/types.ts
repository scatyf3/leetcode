// 前端用到的几种行的形状。只写前端真读的字段 —— 真相在 server.py 的 list_problems / syntax_list。

export type Familiarity = number | null

export interface Problem {
  id: number
  title: string
  difficulty?: string | null
  status?: string
  familiarity?: number | string | null
  structures: string[]
  paradigms: string[]
  techniques: string[]
  complexity?: { time?: string; space?: string } | null
  paused?: string | null
  due?: string | null
  last_review?: string | null
  stability?: number | null
  cluster?: string | null
  [k: string]: unknown
}

/** 语法卡: id 是 "主题/标题" 字符串, ord 是 /api/syntax 里的下标(书写顺序) */
export interface SyntaxCard {
  id: string
  title: string
  due?: string | null
  last_review?: string | null
  paused?: string | null
  ord?: number
  [k: string]: unknown
}

export type Deck = 'problems' | 'syntax'
export type QueueMode = 'fsrs' | 'order' | 'random'

/** edits.jsonl 的一行(只记 diff) */
export interface Edit {
  id: number
  field: string
  from?: unknown
  to?: unknown
  date?: string
  ts?: number
}
