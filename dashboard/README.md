# LeetCode 看板

数据结构 × 算法范式的本地看板。点进每道题：左边 `*.py` 解法，右边可编辑的笔记（保存回磁盘）。

纯 Python 标准库，**零依赖、无需 pip 安装**。

## 运行

```bash
python dashboard/server.py
```

然后打开 http://localhost:8765 （Ctrl+C 停止）。

## 架构

```
每题文件夹/
  meta.json      ← 标签的真相源（git 追踪）：structures / paradigms / techniques / difficulty / status / familiarity
  *.py           ← 解法（面板里按文件名分 tab 展示）
  note.md 等     ← 笔记（面板右侧可编辑，Ctrl+S 保存）

structures/<结构>.md   ← 该数据结构的通用 trick(点板子左侧的组标签打开)
paradigms/<范式>.md    ← 该算法范式的通用 trick(切到「按范式」后同样点组标签)
notes/*.md             ← 跨题笔记 + scratch.md 随想收件箱(右上角 📓 笔记)

dashboard/
  server.py      ← 标准库 http + sqlite 索引 + API
  scaffold.py    ← 题号/题名 → 抓题面 + 建空题目文件夹（TODO 加条目时自动调）
  fetch_desc.py  ← 批量补抓已有文件夹的 problem.html
  index.html / app.js / styles.css   ← 无构建前端
  data.db        ← SQLite 索引，由 meta.json 重建，已 gitignore
  .lc_index.json ← LeetCode 全量题目清单缓存（题号→slug），一周重抓，已 gitignore
```

- **真相在 `meta.json`**：删掉 `data.db` 也不丢标签，`↻ Sync` 会从各文件夹重建索引。
- **新增题目**：右上角 `📋 TODO` 里输入**题号或题名**回车（`105` / `word break`）→ 自动去 LeetCode 抓题面，建好
  `<编号>. <标题>/`（`problem.html` + 空 `sol.py` + `note.md` + `meta.json`，`status: todo`）并直接进看板表。
  离线或抓失败时 todo 照记，只是没建文件夹。命令行等价物：`python dashboard/scaffold.py 105 "word break"`。
  手工建文件夹放解法也行 → 点面板右上角 `↻ Sync` → 它会出现在「未完全打标签」区，点进去填标签即可。
- **新增/修改解法**：详情页左边代码区，**双击进入编辑**、`Ctrl+S` 保存、`Esc` 或点开退出（和右边笔记一套交互）。
  tab 条最后的 `+ 新解法` 输入文件名（不写 `.py` 会自动补）新建一个。
  文件名只收 `.py`，带路径成分的一律拒绝；**名字打一半点开不会留下空文件**——要保存过才落盘。
  题面 tab（`📄 题目`）是只读的。删文件仍然只能在文件系统里做。

## 熟练度 familiarity

`meta.json` 里的 `familiarity`，1–4，`0` / 缺省 = 未评：

| 值 | 含义 | 该怎么处理 |
|----|------|-----------|
| 1 | 已经熟悉 | 只做间隔重刷，别再花时间。**只有盲写一次过才升到这档**——「看着简单」「没留下踩坑记录」都不算 |
| 2 | 思路会，细节容易写错 | 别重看题解，**盲写一遍**，对着 note 里的 bug 清单查 |
| 3 | 思路大概知道，不熟 | 先复述思路再写；写不出来说明卡在「怎么想到」那一步 |
| 4 | 思路都不知道 | 当新题重做，做完补 note |

面板左上角有 `L1 L2 L3 L4` 过滤按钮（可多选，再点一下取消）；
每行标题前的方块是熟练度，圆点是难度 —— **两个不是一回事**，简单题也可以不熟。
详情页「熟练度」下拉改完即存回 `meta.json`。

## 面板怎么用

- 主视图按 **结构** 分组；右上角可切「按范式」，行尾的 chip 自动换成另一个维度。
- 组标签可点开该结构 / 该范式的通用 trick 文档。
- `dp` 拆成了 `1d-dp` / `2d-dp` —— 两者的难点完全不同（找递推 vs 找扫描顺序）。
- **空格子**一眼可见 → 就是你还没覆盖的题型组合，该补哪类题很直观。
- 灰色虚线 chip = `status: todo`；圆点颜色 = 难度（绿易 / 黄中 / 红难）。

## API（供扩展）

| 方法 | 路径 | 作用 |
|------|------|------|
| GET  | `/api/problems`          | 列表（含标签） |
| GET  | `/api/problems/{id}`     | 详情（解法内容 + 笔记） |
| PUT  | `/api/problems/{id}/note`| 保存笔记到磁盘 |
| PUT  | `/api/problems/{id}/solutions/{file.py}` | 新建 / 覆盖一个解法文件 |
| PUT  | `/api/problems/{id}/meta`| 保存标签到 meta.json |
| POST | `/api/problems`          | `{"query": "105"}` 或 `{"query": "word break"}` → 建题目文件夹并入表 |
| POST | `/api/sync`              | 重扫文件夹、重建索引 |

## 线上部署（只读）

`main` 一 push，GitHub Actions 就把看板烤成静态站发到
**https://scatyf3.github.io/leetcode/** —— 别人只能看，只有你能改。

```bash
python dashboard/export_static.py dist   # 本地预览同一份产物
python -m http.server -d dist 8000
```

- `export_static.py` 复用 `server.py` 的那几个 GET 函数，把响应烤成同名 JSON
  （`/api/problems/98` → `api/problems/98.json`），题目详情点开才拉，首屏只有列表。
- `static-shim.js` 把 `fetch` 改道到这些 JSON，写请求就地拒绝；`ro.css` 把编辑入口藏掉。
  **`app.js` 一行没改**，本地跑 `server.py` 还是完整的可写看板。
- `notes/scratch.md` 和 `notes/todo.md` 不上线（`PRIVATE_NOTES`）。
- 线上没有任何写接口存在 —— 不是关掉，是压根没导出。

## 端口

默认 `8765`，改 `server.py` 顶部的 `PORT`。
