---
title: 图的形状
status: draft
order: 3
alias: []
related: [/advanced/cycle-detection, /advanced/functional-graph, /advanced/graph-modeling, /structures/graph]
---

# 图的形状

> 环相关的题先判断图属于哪一类：第一步看整张图的方向和出度，第二步看每个连通块的边数或有向环。类别定了，每块有几个环、剥叶子剩下什么、该拿哪个工具也就定了

## 一句话

先选支，再看每块。每张图、每个连通块都恰好落在一片叶子上，每片叶子下面挂着它的常见题型。

## 怎么用

1. **第一步，看整张图**：边有没有方向；有向的话，是不是每个点最多一条出边。三支互不重叠。
2. **第二步，看每个连通块**：无向数 r = m − n + 1；出度 ≤ 1 比较 m 和 n；其余的有向图看有没有有向环。
3. **第三步，看题目问什么**：在叶子下面找对应的问法，问的东西在环上还是在树上，通常要分开算。

记号：n = 一块的点数，m = 一块的边数，r = 一块里独立环的个数。整张图有多个块时，第二步对每块各做一次，不同的块可以落在不同的叶子上；整张图合计的独立环数是 m − n + c（c = 块数）。

<GraphShapes />

## 原理：为什么这样分

| | 为什么 |
|---|---|
| 前两支只看边数就够 | 出度 ≤ 1 时，去掉方向看到的环一定也是有向环：环上要是有个点两条环边都往外指，它的出度就是 2。所以无向和出度 ≤ 1 两支，数边就等于数环 |
| 出度 ≤ 1 只有两片叶子 | 有出边的点各贡献一条边，所以 m = n − （出边是 −1 的点数）。连通至少要 n − 1 条边，所以出边是 −1 的点最多一个：有一个是内向树，没有就是函数图块 |
| 第三支不能看边数 | 0→1、1→2、0→2 去掉方向是个三角形，m = n，但它没有有向环，是 DAG。方向会让边数失效，只能直接判有没有有向环 |

> (m, n, c) 三个总数只能定出整张图的独立环数 m − n + c。环分在哪几块、有没有方向，都看不出来；只有出度 ≤ 1 这一支能用它们把每块的类别完全定死。

## 每种形状

### 树 {#tree}

**条件**：无向，r = 0（m = n − 1）　**保证**：任意两点之间恰好一条路径；剥度为 1 的点能剥光，最后剩下的 1–2 个点是中心

**工具**：DFS 子树 DP、换根、剥叶子找中心　**细讲**：[树](../structures/tree)

| 问法 | 解法 | 例题 |
|---|---|---|
| 是不是一棵树 | m = n − 1 并且连通；或者并查集一路没成环 | [261](https://leetcode.com/problems/graph-valid-tree/) |
| 最矮的根 / 中心 | 剥度为 1 的点，一层层剥，最后剩下的 1–2 个就是中心 | [310](https://leetcode.com/problems/minimum-height-trees/) |
| 直径 / 最长路径 | 两次 BFS：从任意点走到最远点 a，再从 a 走到最远点；或子树 DP 记最长的两条链 | [1245](https://leetcode.com/problems/tree-diameter/) · [543](https://leetcode.com/problems/diameter-of-binary-tree/) |
| 每个点当根的答案 | 换根 DP：第一遍 DFS 算子树信息，第二遍从父亲推到孩子 | [834](https://leetcode.com/problems/sum-of-distances-in-tree/) |

### 基环树 {#pseudo}

**条件**：无向，r = 1（m = n）　**保证**：恰好一个环；多出来的那条边一定在环上；剥度为 1 的点，剩下的恰好是环

**工具**：并查集找闭环边、剥叶子拿环　**细讲**：[判环](./cycle-detection) §4

| 问法 | 解法 | 例题 |
|---|---|---|
| 哪条边是多出来的 | 并查集，第一条两端早就连通的边 | [684](https://leetcode.com/problems/redundant-connection/) |
| 找出环 / 点到环的距离 | 剥度为 1 的点剩下环；环上的点距离为 0，从它们一起多源 BFS | [2204](https://leetcode.com/problems/distance-to-a-cycle-in-undirected-graph/) |
| 基环树上做 DP | 断开环上一条边，变成一棵树；断边两端分情况各做一遍树形 DP。213 是只有环、没有树的版本 | [213](https://leetcode.com/problems/house-robber-ii/) |

### 一般无向图 {#graph}

**条件**：无向，r ≥ 2　**保证**：取一棵生成树，剩下 r 条非树边，每条闭上一个环；剥度为 1 的点剩下 2-core

**工具**：并查集判环、每点 BFS 求最短环、Tarjan 求桥　**细讲**：[判环](./cycle-detection) §3、§4

| 问法 | 解法 | 例题 |
|---|---|---|
| 连通块个数 / 合并 | 并查集，或每个没访问过的点 DFS 一次 | [323](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/) |
| 有没有环 | 并查集：加边前两端已连通；DFS：碰到不是父亲的已访问点 | [1559](https://leetcode.com/problems/detect-cycles-in-2d-grid/) |
| 最短环 | 每个点做一次 BFS，非树边给出候选 dist[u] + dist[v] + 1，取最小 | [2608](https://leetcode.com/problems/shortest-cycle-in-a-graph/) |
| 能不能二分（有没有奇环） | BFS 染色，相邻两点同色就冲突；冲突 ⇔ 有奇环 | [785](https://leetcode.com/problems/is-graph-bipartite/) |
| 桥 / 割点 | Tarjan：DFS 记 dfn 和 low，看子树能不能绕非树边回到上面 | [1192](https://leetcode.com/problems/critical-connections-in-a-network/) |

### 内向树 {#intree}

**条件**：出度 ≤ 1，m = n − 1　**保证**：块里正好一个点出边是 −1，它就是根；并查集的 parent 数组就是内向树森林

**工具**：倍增求祖先 / LCA、按深度倒序做 DP　**细讲**：[并查集](../paradigms/union-find)

| 问法 | 解法 | 例题 |
|---|---|---|
| 第 k 个祖先 | 倍增：up[j][v] 由两次 up[j − 1] 拼出；k 按二进制位往上跳 | [1483](https://leetcode.com/problems/kth-ancestor-of-a-tree-node/) |
| 两点的最近公共祖先 | 两条往根走的链表求交点；或者先对齐深度再一起往上走 | [1650](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree-iii/) |
| 每个点到根的路径和 | 沿 parent 记忆化：dist[v] = w[v] + dist[parent[v]] | [1376](https://leetcode.com/problems/time-needed-to-inform-all-employees/) |
| 子树聚合（大小、得分） | 建孩子表做 DFS；或按入度剥叶子，把孩子的值推给父亲 | [2049](https://leetcode.com/problems/count-nodes-with-the-highest-score/) |

### 函数图块 {#func}

**条件**：出度 ≤ 1，m = n　**保证**：ρ 形：正好一个有向环，树挂在环上；按入度剥叶子，剩下的恰好是环

**工具**：时间戳、剥叶子、Floyd、倍增　**细讲**：[函数图](./functional-graph)

| 问法 | 解法 | 例题 |
|---|---|---|
| 找环 / 最长环 | 时间戳：撞到这一轮编过号的点，环长 = 当前时钟 − 它的时间戳 | [2360](https://leetcode.com/problems/longest-cycle-in-a-graph/) |
| 每个点能走到几个点 / 到环的距离 | 剥叶子分开环和树；环上的点看环长，树上的点按剥的顺序倒着推 ans[u] = ans[f(u)] + 1 | [2876](https://leetcode.com/problems/count-visited-nodes-in-a-directed-graph/) |
| 用环和链拼答案 | 按环长分类讨论；剥叶子时顺手记进每个点的最长链 | [2127](https://leetcode.com/problems/maximum-employees-to-be-invited-to-a-meeting/) |
| 走 k 步，k 很大 | 倍增；或者算出尾巴 + 整圈数 + 余数 | [2836](https://leetcode.com/problems/maximize-value-of-function-in-a-ball-passing-game/) |
| 单个起点的入环点 | Floyd 快慢指针：相遇后一个回起点，两个同速走，再相遇的点就是入环点 | [287](https://leetcode.com/problems/find-the-duplicate-number/) · [142](https://leetcode.com/problems/linked-list-cycle-ii/) |
| 两个起点的最近汇合点 | 从两个起点各走一遍记 dist（只有一条路），再挑 max 最小的点 | [2359](https://leetcode.com/problems/find-closest-node-to-given-two-nodes/) |

### 置换 {#perm}

**条件**：函数图块，入度也都是 1　**保证**：只有环、没有树；排序最少交换次数 = n − 环数

**工具**：沿 i → p[i] 数环　**细讲**：—

| 问法 | 解法 | 例题 |
|---|---|---|
| 排序最少交换几次 | 当前位置指向排好序后的位置，答案 = n − 环数 | [2471](https://leetcode.com/problems/minimum-number-of-operations-to-sort-a-binary-tree-by-level/) |
| 原地归位 / 找缺失的数 | 环排序：把 x 一路换到它该在的位置 | [41](https://leetcode.com/problems/first-missing-positive/) · [448](https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/) |
| 重复几次回到原样 | 每个环各转各的，周期 = 各环长的 lcm | [1806](https://leetcode.com/problems/minimum-number-of-operations-to-reinitialize-a-permutation/) |

### DAG {#dag}

**条件**：有点出度 ≥ 2，没有有向环　**保证**：存在拓扑序；按入度能剥光；沿拓扑序 DP 不会循环依赖

**工具**：Kahn、拓扑序 DP　**细讲**：[BFS](../paradigms/bfs) §6、[建图](./graph-modeling)

| 问法 | 解法 | 例题 |
|---|---|---|
| 排出一个顺序 | Kahn：入度为 0 的点入队，剥出来的顺序就是拓扑序 | [210](https://leetcode.com/problems/course-schedule-ii/) · [2392](https://leetcode.com/problems/build-a-matrix-with-conditions/) |
| 最长路径 / 路径计数 | 沿拓扑序 DP，每个点的值由所有前驱推出来 | [2050](https://leetcode.com/problems/parallel-courses-iii/) · [1857](https://leetcode.com/problems/largest-color-value-in-a-directed-graph/) |
| 谁是谁的前置（传递关系） | 沿拓扑序把每个点的前置集合传给后继 | [1462](https://leetcode.com/problems/course-schedule-iv/) |
| 网格里严格单调地走 | 边从小指向大，天然无环，是隐式 DAG；记忆化 DFS 即可 | [329](https://leetcode.com/problems/longest-increasing-path-in-a-matrix/) |

### 一般有向图 {#digraph}

**条件**：有点出度 ≥ 2，有有向环　**保证**：有环 ⇔ DFS 有边指向灰点；按入度剥剩环和下游，按出度剥剩环和上游；SCC 缩点后是 DAG

**工具**：三色 DFS、Kahn 正反向、SCC 缩点　**细讲**：[判环](./cycle-detection) §1、§2

| 问法 | 解法 | 例题 |
|---|---|---|
| 有没有环 / 能不能全部完成 | Kahn 剥不完就有环；或三色 DFS 碰到指向灰点的边 | [207](https://leetcode.com/problems/course-schedule/) |
| 哪些点永远走不进环 | 建反图，按出度剥，能剥掉的就是 | [802](https://leetcode.com/problems/find-eventual-safe-states/) |
| 有向最短环 | 每个点 BFS，第一条指回起点的边 u → s 给出 dist[u] + 1 | — |
| 环上的点要当成一个整体 | SCC 缩点后变成 DAG，再套 DAG 的题型。LC 少见，CF 常见 | — |

## 两条统一规律

### 剥叶子：剩下的是什么

| 怎么剥 | 一般情况剩下 | 特例 | 题 |
|---|---|---|---|
| 有向，按入度 | 环 + 从环出发能走到的点 | DAG 剥光，顺序就是拓扑序；函数图块剩下**恰好是环** | 207 · 210 · 2876 · 2127 |
| 有向，按出度（反图） | 环 + 能走进环的点 | 剥掉的点 = 永远走不进环的点 | 802 |
| 无向，按度 = 1 | 2-core：环和连接环的路 | 树剥光，最后 1–2 个点是中心；基环树剩下**恰好是环** | 310 · 2204 |

### 遍历：哪种边闭上环

| 形状 | 算环的边 | 要记的状态 | 题 |
|---|---|---|---|
| 无向 / 网格 | 任何不回父亲的非树边 | 来过没有 + 父亲，或直接并查集 | 684 · 1559 |
| 无向，求最短环 | 同上，候选 `dist[u]+dist[v]+1` | 每个起点一次 BFS | 2608 |
| 一般有向 | 指向**灰点**的边；指向黑点的不算 | 三色：白 / 灰 / 黑 | 207 |
| 出度 ≤ 1 | 指向这一轮编过号的点 | 时间戳 + `round_begin`（三色的特化） | 2360 |

> 走 k 步的倍增是 [快速幂](./modular) 那条线，只是题目出在函数图上。

## 栽过的坑

只收自己真栽过的。
