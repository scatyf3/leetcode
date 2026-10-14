import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import LayerFigure from './components/LayerFigure.vue'
import LayerIndex from './components/LayerIndex.vue'
import StructureMap from './components/StructureMap.vue'
import ProblemList from './components/ProblemList.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  // 每篇正文后面挂上 tracker 里打了这个标签的题（index 页和 python 层渲染为空）
  Layout: () => h(DefaultTheme.Layout, null, { 'doc-after': () => h(ProblemList) }),
  enhanceApp({ app }) {
    app.component('LayerFigure', LayerFigure)
    app.component('LayerIndex', LayerIndex)
    app.component('StructureMap', StructureMap)
  },
} satisfies Theme
