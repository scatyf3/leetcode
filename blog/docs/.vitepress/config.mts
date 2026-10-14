import { defineConfig } from 'vitepress'
import { buildSidebar } from './sidebar'

// 和看板挂在同一个 GitHub Pages 站下：/leetcode/ 是看板，/leetcode/blog/ 是这里
const BASE = '/leetcode/blog/'

export default defineConfig({
  lang: 'zh-CN',
  title: 'LeetCode Blog',
  description: '刷题知识库：Python 内置 → 概念数据结构 → 算法套路',
  base: BASE,
  cleanUrls: true,
  lastUpdated: true,
  // 坏链直接让构建失败；指向题目文件夹 / notes 的链接一律写 GitHub 绝对地址
  ignoreDeadLinks: false,
  markdown: { lineNumbers: false },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: 'Python', link: '/python/' },
      { text: '结构', link: '/structures/' },
      { text: '套路', link: '/paradigms/' },
      { text: '看板', link: 'https://scatyf3.github.io/leetcode/' },
    ],
    sidebar: buildSidebar(),
    search: { provider: 'local', options: { detailedView: true } },
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    lastUpdated: { text: '最后更新' },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题',
    socialLinks: [{ icon: 'github', link: 'https://github.com/scatyf3/leetcode' }],
  },
})
