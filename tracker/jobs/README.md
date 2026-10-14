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

## 盯板子: `watch_boards.py`

```bash
python3 jobs/watch_boards.py --discover   # 第一次: 猜出每家的 board 地址并记下
python3 jobs/watch_boards.py              # 扫一遍, 只打印新增的 entry / new grad 岗
python3 jobs/watch_boards.py --write      # 顺便把 ng 标记写回看板
```

**为什么需要它:各家的 new grad 窗口不同步。** Airbnb 的 new grad 岗是 2026 年
3–4 月发的,到 9 月已经下架、板上只剩 Staff 起步;而大厂 SDE 的秋招坑 9–10 月才开。
按一个统一窗口去排必然系统性错过一批。一天扫一次,谁什么时候开都接得住。

Greenhouse 和 Ashby 的 job board 都有**公开 JSON API**,不需要 key:

```
https://boards-api.greenhouse.io/v1/boards/<slug>/jobs
https://api.ashbyhq.com/posting-api/job-board/<slug>
```

所以不要去查聚合站(Glassdoor / builtin / jobright 那些)—— 过期和转载混在一起,
分不出「招完了」和「还没开」。板子是唯一权威口径。

每家的地址存在记录的 `board` 字段(`greenhouse:airbnb` / `ashby:modal` / `-` 表示
没有或猜不到),`--discover` 猜不出来的可以在详情弹窗里手填。

历史存在 `jobs/data/boards.json`(gitignore),每个岗位记 `first_seen` ——
**攒几个月就有了一张「谁什么时候开坑」的表**,这正是排 timeline 需要、而聚合站给不了的。

岗位分两桶:`ng`(标题明说 new grad / 校招)和 `entry`(工程岗但不带
Senior / Staff / Principal 前缀)。带 SRE / on-call / production support 的一律不要 ——
理由见分组说明里的定位粘性。

## 只读站

```bash
python jobs/export_static.py dist/jobs
```

`.github/workflows/pages.yml` 里已经串好了,push 到 main 自动发到
`https://scatyf3.github.io/leetcode/jobs/`。

## 坑

**后端不热重载。** 改了 `server.py` 要 Ctrl+C 重启;只改 `app.js` / `styles.css` 刷新浏览器就够了
(响应带了 `Cache-Control: no-store`)。和 dashboard 一个坑。

## 公司 vs 岗位

**公司一行 = 一条投递流程**,也就是漏斗的分母。**岗位(jd)是它的明细** ——
同一个 ATS 下的几个 req 拆成几条挂在公司下面,公司仍然只算一家。

这么分是因为漏斗算的是转化:一家公司投了 3 个岗、面试只走一次,如果拆成 3 行,
`pool` 变 3 而 `applied` 只有 1,C1 就被稀释成 33%,而它本该是 100%。

    公司       tier / status / outcome / applied / 漏斗
      └ 岗位   role / url / loc / lv / note / pick

`pick` 是主岗 —— 公司那一行显示的、导出静态站时用的那条,每家唯一。
后端在任何一次岗位增删改之后把它同步回公司的 `role` / `url`,所以老的导出路径不用改。

什么时候该开**第二行公司**而不是第二条岗位:两者走**独立的投递流程**时。
`nvidia` / `nvidia-2`(美国 / 中国区)就是这种 —— 不同法人主体、不同 tier、
各自算漏斗。同一个 ATS 下的并列 req 一律用岗位,不开新行。

接口:

    POST   /api/apps/<id>/jds            加一条(第一条自动成为主岗)
    PUT    /api/apps/<id>/jds/<jid>      改 role/url/loc/lv/note;{"pick":1} 设主岗
    DELETE /api/apps/<id>/jds/<jid>      删(删掉主岗则顺位补上)

`lv` 的取值和 `scan_board.py` / `watch_boards.py` 的分桶用同一套词:
`ng` / `mid` / `sr` / 空。
