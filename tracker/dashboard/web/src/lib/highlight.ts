import { esc } from './esc'

// ---- python syntax highlighter (tokenizer, no external deps) ----
const PY_KW = new Set(['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break',
  'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
  'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
  'while', 'with', 'yield', 'match', 'case'])
const PY_BUILTIN = new Set(['print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'set',
  'tuple', 'bool', 'sorted', 'sum', 'min', 'max', 'abs', 'enumerate', 'zip', 'map', 'filter', 'open',
  'input', 'type', 'isinstance', 'super', 'object', 'Exception', 'self', 'cls', 'None', 'True', 'False'])

export function highlightPython(src: string): string {
  let i = 0, out = '', prevWord = ''
  const n = src.length
  const push = (cls: string | null, txt: string) =>
    (out += cls ? `<span class="t-${cls}">${esc(txt)}</span>` : esc(txt))
  while (i < n) {
    const c = src[i]
    if (c === '#') {                                   // comment
      let j = i; while (j < n && src[j] !== '\n') j++
      push('com', src.slice(i, j)); i = j; continue
    }
    if ((c === '"' || c === "'") && src.substr(i, 3) === c + c + c) {  // triple string
      const q = c + c + c; let j = i + 3
      while (j < n && src.substr(j, 3) !== q) j++
      j = Math.min(n, j + 3); push('str', src.slice(i, j)); i = j; continue
    }
    if (c === '"' || c === "'") {                      // single/double string
      let j = i + 1; while (j < n && src[j] !== c) { if (src[j] === '\\') j++; j++ }
      j = Math.min(n, j + 1); push('str', src.slice(i, j)); i = j; continue
    }
    if (/[0-9]/.test(c) || (c === '.' && /[0-9]/.test(src[i + 1] || ''))) {  // number
      let j = i; while (j < n && /[0-9a-fA-FxXoObB._]/.test(src[j])) j++
      push('num', src.slice(i, j)); i = j; continue
    }
    if (c === '@') {                                   // decorator
      let j = i + 1; while (j < n && /[A-Za-z0-9_.]/.test(src[j])) j++
      push('dec', src.slice(i, j)); i = j; continue
    }
    if (/[A-Za-z_]/.test(c)) {                         // identifier / keyword
      let j = i; while (j < n && /[A-Za-z0-9_]/.test(src[j])) j++
      const w = src.slice(i, j)
      const cls = PY_KW.has(w) ? 'kw'
        : (prevWord === 'def' || prevWord === 'class') ? 'fn'
          : PY_BUILTIN.has(w) ? 'bi' : null
      push(cls, w); prevWord = w; i = j; continue
    }
    if (!/\s/.test(c)) prevWord = ''                   // reset on real punctuation
    push(null, c); i++
  }
  return out
}
