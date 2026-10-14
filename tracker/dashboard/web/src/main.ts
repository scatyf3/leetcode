// 入口: 字体 + 样式 + 主题开关, 然后把看板跑起来(app.js 顶层就会 reload())。
// 字体打进产物, 不走 Google Fonts —— 本地看板断网也要长一个样。
import '@fontsource-variable/inter'
import './styles.css'
import { initTheme } from './theme'
import './app.js'

initTheme()
