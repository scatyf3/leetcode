import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import LayerFigure from './components/LayerFigure.vue'
import LayerIndex from './components/LayerIndex.vue'
import StructureMap from './components/StructureMap.vue'
import ProblemList from './components/ProblemList.vue'
import TopicFamily from './components/TopicFamily.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  // 每篇正文后面挂上 tracker 里打了这个标签的题（index 页和 python 层渲染为空）；
  // 正文前面标出套路的父子关系（frontmatter 的 parent）
  Layout: () => h(DefaultTheme.Layout, null, {
    'doc-before': () => h(TopicFamily),
    'doc-after': () => h(ProblemList),
  }),
  enhanceApp({ app }) {
    app.component('LayerFigure', LayerFigure)
    app.component('LayerIndex', LayerIndex)
    app.component('StructureMap', StructureMap)
  },
} satisfies Theme
