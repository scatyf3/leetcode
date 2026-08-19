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
  meta.json      ← 标签的真相源（git 追踪）：structures / paradigms / techniques / difficulty / status
  *.py           ← 解法（面板里按文件名分 tab 展示）
  note.md 等     ← 笔记（面板右侧可编辑，Ctrl+S 保存）

dashboard/
  server.py      ← 标准库 http + sqlite 索引 + API
  index.html / app.js / styles.css   ← 无构建前端
  data.db        ← SQLite 索引，由 meta.json 重建，已 gitignore
```

- **真相在 `meta.json`**：删掉 `data.db` 也不丢标签，`↻ Sync` 会从各文件夹重建索引。
- **新增题目**：建一个 `<编号>. <标题>/` 文件夹放解法 → 点面板右上角 `↻ Sync` → 它会出现在「未完全打标签」区，点进去填标签即可。

## 面板怎么用

- 主视图是 **结构（行）× 范式（列）** 的矩阵，一题可同时出现在多个格子（多标签）。
- **空格子**一眼可见 → 就是你还没覆盖的题型组合，该补哪类题很直观。
- 灰色虚线 chip = `status: todo`；圆点颜色 = 难度（绿易 / 黄中 / 红难）。

## API（供扩展）

| 方法 | 路径 | 作用 |
|------|------|------|
| GET  | `/api/problems`          | 列表（含标签） |
| GET  | `/api/problems/{id}`     | 详情（解法内容 + 笔记） |
| PUT  | `/api/problems/{id}/note`| 保存笔记到磁盘 |
| PUT  | `/api/problems/{id}/meta`| 保存标签到 meta.json |
| POST | `/api/sync`              | 重扫文件夹、重建索引 |

## 端口

默认 `8765`，改 `server.py` 顶部的 `PORT`。
