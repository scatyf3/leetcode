// 所有请求都走绝对路径 /api/...: 本地是 server.py, 只读站由 public/static-shim.js 改道到导出的 .json
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const api = <T = any>(u: string, opt?: RequestInit): Promise<T> => fetch(u, opt).then((r) => r.json())

export const postJSON = <T = any>(u: string, body: unknown, method = 'POST') =>
  api<T>(u, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

/** 只读静态站: static-shim.js 会在 <html> 上挂 .ro */
export const isReadOnly = () => document.documentElement.classList.contains('ro')
