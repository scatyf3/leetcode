const ESC: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }

/** 拼 innerHTML 时的转义。单引号不转 —— 全站属性值一律用双引号包 */
export function esc(s: unknown): string {
  return String(s).replace(/[&<>"]/g, (c) => ESC[c])
}
