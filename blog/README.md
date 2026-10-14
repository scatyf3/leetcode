# LeetCode Blog

刷题知识库，三层，VitePress。站点：<https://scatyf3.github.io/leetcode/blog/>

```
L3 paradigms/   算法套路   题型 → 模板 → 坑
L2 structures/  概念结构   每多维护一种信息就多一种结构（推导图在 /structures/）
L1 python/      Python 内置 这个 API 底下是什么，复杂度从哪来
```

## 本地

```bash
cd blog
npm install
npm run docs:dev      # http://localhost:5173/leetcode/blog/
npm run docs:build    # ignoreDeadLinks: false，坏链会让构建失败
```

## 写一篇

复制 `templates/topic.md` 到对应层的目录，填 frontmatter。sidebar 和首页分层图都从 frontmatter 生成，
层本身定义在 `docs/.vitepress/layers.ts`（唯一手工维护的结构信息）。

每篇底部自动列出 `tracker/<题>/meta.json` 里打了这个标签的题：structures 层对 `structures` 字段，
paradigms 层对 `paradigms` 字段，匹配文件名或 `alias`。按熟练度从生到熟排。

## 和 tracker 的关系

- `structures/`、`paradigms/` 这两层同时也是看板里点组标题打开的 trick 文档 ——
  `tracker/dashboard/server.py` 直接读写这里，读的时候剥掉 frontmatter，写回时接上。
- 指向题目文件夹、`tracker/notes/`、`tracker/syntax/` 的链接写 GitHub 绝对地址
  （`https://github.com/scatyf3/leetcode/blob/main/tracker/...`），不然 VitePress 当坏链。
- tracker 那边指过来用相对路径 `../../blog/docs/structures/x.md`。
