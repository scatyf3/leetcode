// 深色 / 浅色。<html data-theme> 是唯一开关, 首帧前由 index.html 里那段内联脚本落定。
// 手动点过就记在 localStorage('lc-theme'), 没点过就一直跟着系统走(系统切了这里也跟着切)。
type Theme = 'light' | 'dark'

const KEY = 'lc-theme'
const media = matchMedia('(prefers-color-scheme: dark)')

function saved(): Theme | null {
  try {
    const t = localStorage.getItem(KEY)
    return t === 'light' || t === 'dark' ? t : null
  } catch { return null }
}

const current = (): Theme => (document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light')

function apply(t: Theme) {
  document.documentElement.dataset.theme = t
  const btn = document.getElementById('theme-toggle')
  if (btn) {
    btn.setAttribute('aria-checked', String(t === 'dark'))
    btn.title = t === 'dark' ? '切到浅色' : '切到深色'
  }
}

export function initTheme() {
  apply(saved() || (media.matches ? 'dark' : 'light'))
  media.addEventListener('change', (e) => { if (!saved()) apply(e.matches ? 'dark' : 'light') })
  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const next: Theme = current() === 'dark' ? 'light' : 'dark'
    try { localStorage.setItem(KEY, next) } catch { /* 隐私模式: 这一页内照样切 */ }
    apply(next)
  })
}
