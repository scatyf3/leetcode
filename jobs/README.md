# 求职看板

AI infra 求职的**三组分层 + 8 周时间线**。和 LeetCode 看板同一套架构:纯 Python 标准库、
无构建前端、Vue 从 `vendor/` 本地加载,**零依赖、无需 pip 安装**。

```bash
python jobs/server.py        # http://localhost:8766
```

(端口是 **8766**,不是 dashboard 的 8765 —— 两个看板要能同时开着。)

## 四个视图

| 视图 | 答的问题 |
|---|---|
| **时间线**(首屏) | 这周该投哪一档、投几家?进度落后没有? |
| **公司** | 每家现在到哪一步了?内推到位没?OA 哪天截止? |
| **漏斗** | 三层转化率各是多少、对着先验是高是低?**问题在哪一层?** |

首屏落在时间线,因为一开页要先答「这周该干什么」;漏斗是发现节奏不对之后的第二跳。
切过一次就记住(`localStorage` 的 `jb-view`)。

## 隐私:为什么真相分两半

**这个仓库是 public 的。** 所以数据按敏感度切开:

```
jobs/plan.json                ← 计划 + 候选池。git 追踪 → 上 Pages。手改这个文件就是改计划
jobs/data/applications.json   ← 你的投递状态。**已 gitignore,永不出仓库**
jobs/data/events.jsonl        ← 每次状态流转追加一行(只记 diff),同样 gitignore
```

线上那份是「C/B/A 怎么分、8 周怎么排」,不是「我投了谁、被谁拒了」。
`export_static.py` 里的 `EXPORT_APPLICATIONS = False` 是唯一的开关 ——
默认导出的 `api/apps.json` 是个空壳,公开站的时间线和漏斗就是一排 0,方法那页是全的。

想连状态一起公开再改那个 `False`,但想清楚:**公司名 + 「被拒」+ 内推人,是会被搜索引擎索引的。**

## 数据模型

一家公司一条记录,两个正交的字段描述它在哪:

- `status` —— **到达过的最高阶段**,单调推进:`pool → applied → oa → screen → onsite`
- `outcome` —— **结局**,和阶段正交:`""`(在跑)/ `offer` / `rejected` / `withdrawn`

拆成两个是因为「OA 阶段被拒」和「onsite 阶段被拒」在漏斗里必须落到不同的层 ——
用一个 `status` 字段表示不了「走到哪儿挂的」,而那正是漏斗要诊断的东西。

`referral` 单独一列(`none / asked / got`),因为它是转化率里最大的杠杆:
同一家公司带不带内推,首响率差 4 倍(12% vs 3%)。

## 加公司

两个入口,用途不同:

- **改 `plan.json` 的 `pool`** —— 加进候选池。下次启动 server 会自动补进 `applications.json`,
  **不会覆盖你已有的状态**。适合成批加、也会跟着上 Pages(所以别在这写私人备注)。
- **看板右上角输入框** —— 临时加一家,只进本地 `applications.json`,不进 git。

## 只读站

```bash
python jobs/export_static.py dist/jobs
```

`.github/workflows/pages.yml` 里已经串好了,push 到 main 自动发到
`https://scatyf3.github.io/leetcode/jobs/`。

## 坑

**后端不热重载。** 改了 `server.py` 要 Ctrl+C 重启;只改 `app.js` / `styles.css` 刷新浏览器就够了
(响应带了 `Cache-Control: no-store`)。和 dashboard 一个坑。
