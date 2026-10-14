// 全部按**本地日期**算, 和 server.py 的 today_str() 是同一套口径。
// 'sv' locale 的日期格式正好是 YYYY-MM-DD。

export const todayStr = () => new Date().toLocaleDateString('sv')

export const dParse = (s: string) => {
  const [y, m, d] = s.split('-').map(Number)
  return new Date(y, m - 1, d)
}
export const dAdd = (s: string, n: number) => {
  const t = dParse(s)
  t.setDate(t.getDate() + n)
  return t.toLocaleDateString('sv')
}
export const mmdd = (s: string) => s.slice(5).replace('-', '/')

/** 一周从周一算 */
export const weekStart = (d: string) => {
  const t = dParse(d)
  const k = (t.getDay() + 6) % 7
  return dAdd(d, -k)
}

export const daysSince = (d: string, today = todayStr()) =>
  Math.round((new Date(today).getTime() - new Date(d).getTime()) / 864e5)

/** "下次什么时候" —— 0 说成今天 */
export function fmtInterval(days: number) {
  if (days <= 0) return '今天'
  if (days === 1) return '明天'
  if (days < 30) return `${days} 天`
  if (days < 365) return `${(days / 30).toFixed(1)} 个月`
  return `${(days / 365).toFixed(1)} 年`
}

/** 记忆强度和间隔用 —— fmtInterval 会把 0 说成"今天", 这里不合适 */
export function fmtDays(d: number) {
  if (!d || d <= 0) return '—'
  if (d < 1) return '<1 天'
  if (d < 30) return `${d.toFixed(d < 10 ? 1 : 0)} 天`
  if (d < 365) return `${(d / 30).toFixed(1)} 个月`
  return `${(d / 365).toFixed(1)} 年`
}
