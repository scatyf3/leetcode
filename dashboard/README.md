# LeetCode 看板

本地看板，两个视图：

- **矩阵** — 数据结构 × 算法范式。点进每道题：左边 `*.py` 解法，右边可编辑的笔记（保存回磁盘）。
- **坐标系** — 覆盖 × 深度。备考进度盘：题单铺到哪一层 × 每题掌握到哪一级，叠上时间线。

纯 Python 标准库，**零依赖、无需 pip 安装**。

## 运行

```bash
python dashboard/server.py
```

然后打开 http://localhost:8765 （Ctrl+C 停止）。

## 架构

```
每题文件夹/
  meta.json      ← 标签的真相源（git 追踪）：structures / paradigms / techniques / difficulty / status
  *.py           ← 解法（面板里按文件名分 tab 展示）
  note.md 等     ← 笔记（面板右侧可编辑，Ctrl+S 保存）

dashboard/
  server.py      ← 标准库 http + sqlite 索引 + API
  index.html / app.js / styles.css   ← 无构建前端
  data.db        ← SQLite 索引，由 meta.json 重建，已 gitignore
  plan.json      ← 坐标系视图的分层 + 时间线（手改）
  progress.json  ← 每题掌握度 0..3（面板点击写回，git 追踪）
```

- **真相在 `meta.json`**：删掉 `data.db` 也不丢标签，`↻ Sync` 会从各文件夹重建索引。
- **新增题目**：建一个 `<编号>. <标题>/` 文件夹放解法 → 点面板右上角 `↻ Sync` → 它会出现在「未完全打标签」区，点进去填标签即可。

## 视图一：矩阵

- **结构（行）× 范式（列）**，一题可同时出现在多个格子（多标签）。
- **空格子**一眼可见 → 就是你还没覆盖的题型组合，该补哪类题很直观。
- 灰色虚线 chip = `status: todo`；圆点颜色 = 难度（绿易 / 黄中 / 红难）。

回答的问题是：**哪类题型组合我还没碰过。**

## 视图二：坐标系

回答的问题是：**现在该站哪一格。** 和矩阵视图正交 —— 那个管题型覆盖面，这个管备考进度。

两个轴：

| 轴 | 取值 | 含义 |
|----|------|------|
| 深度（列） | S1 / S2 / S3 | 思路清楚 → 写得对 → 英语讲得清。S1→S2 是 OA 门槛，S2→S3 是面试门槛 |
| 覆盖（行） | 第一/二/三层 | 题单铺到 ≈75 / ≈110 / ≈150 题 |

- 每题只带**一个** stage（`progress.json` 里就是一个 0..3 的数），不是三个独立勾选。
- **深度轴累计**：每格 = 该层里达到该级**及以上**的题数。S3 的题同时计进 S1/S2 列，反过来不成立。
  这才对得上「S2 是 OA 门槛」的读法 —— 问「能过 OA 的有几题」，答案得把讲得清的那些也算上。
- **覆盖轴不累计**：每题只属于一层，第二层那行的分母是它自己的 33 题，不是 110。
  `累计 110` 说的是「题单铺到这一层时总共 110 题」，是计划规模，不是那一行的分母。
- **琥珀框** = 当前阶段该站的格子，跟着日期自己走；过去阶段的目标格降成灰徽章。
- 底下按 pattern group 列题，**点一下循环** `— → S1 → S2 → S3`，立刻写回 `progress.json`。
- **灰掉的组**（Math & Geometry / Bit Manipulation）在第三层里低优先：迁移性最低、OA 命中率最低，时间不够先砍它们。
  第三层内部的取舍顺序是 2-D DP > Advanced Graphs > Greedy > 这两组，从后往前砍。

### 为什么掌握度不放 meta.json

`meta.json` 是「这道题」的真相源，但计划覆盖 150 题，其中大半还没有文件夹。
所以掌握度单独放 `dashboard/progress.json`，一个文件、git 追踪、可 diff。
`meta.json` 的 `status` 是**做没做过**，`progress.json` 的 stage 是**掌握到哪一级**，两件事。

### 改计划

直接编辑 `plan.json` —— 分层、时间线、每组题都在里面，刷新页面即生效：

- `tiers` / `groups[].tier` — 哪些 group 算第几层
- `phases` — 时间线四段的日期、周投入、目标、说明
- `targets` — 哪个阶段该点亮哪个格子（`{phase, tier, stage}`）

## API（供扩展）

| 方法 | 路径 | 作用 |
|------|------|------|
| GET  | `/api/problems`          | 列表（含标签） |
| GET  | `/api/problems/{id}`     | 详情（解法内容 + 笔记） |
| PUT  | `/api/problems/{id}/note`| 保存笔记到磁盘 |
| PUT  | `/api/problems/{id}/meta`| 保存标签到 meta.json |
| POST | `/api/sync`              | 重扫文件夹、重建索引 |
| GET  | `/api/plan`              | 坐标系的分层 + 时间线 |
| GET  | `/api/progress`          | `{stages: {id: 1..3}}` |
| PUT  | `/api/progress`          | `{id, stage}`，`stage=0` 清除 |

## 端口

默认 `8765`，改 `server.py` 顶部的 `PORT`。
