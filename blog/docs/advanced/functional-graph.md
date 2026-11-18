---
title: 函数图
status: draft
order: 3
alias: []
related: [/paradigms/dfs, /structures/graph]
---

# 函数图

> 每个点只有一条出边，图就只能长成「环 + 挂在环上的树」；用时间戳一遍找出所有环，用剥叶子把树和环分开，用倍增走 $10^{10}$ 步

## 一句话

每个点恰好一条出边。从任意一个点一直往下走，最后一定会走进一个环。

## 怎么认出这类题

输入是一个数组 `edges[i]` / `favorite[i]` / `receiver[i]`，意思是点 i 指向另一个点。

建在 L3 的：[DFS](../paradigms/dfs) · [图](../structures/graph)

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| [2360. Longest Cycle in a Graph](https://leetcode.com/problems/longest-cycle-in-a-graph/) | 函数图入门：找环 |
| [2876. Count Visited Nodes in a Directed Graph](https://leetcode.com/problems/count-visited-nodes-in-a-directed-graph/) | 每个点出发能走到几个不同的点 |
| **[2127. Maximum Employees to Be Invited to a Meeting](https://leetcode.com/problems/maximum-employees-to-be-invited-to-a-meeting/)** | 环的大小不同，答案的形状也不同 |
| [2836. Maximize Value of Function in a Ball Passing Game](https://leetcode.com/problems/maximize-value-of-function-in-a-ball-passing-game/) | k ≤ 10¹⁰：先看数据范围 |

## 原理

### 1. 从一个点一直走，一定走进环

**定义**：$n$ 个点，每个点 $i$ 恰好一条出边 $i \to f(i)$。这就是一个函数 $f: \{0, \dots, n-1\} \to \{0, \dots, n-1\}$ 画成的图，所以叫函数图。

**引理 1**：从任意点 $x$ 出发一直走，$x, f(x), f^2(x), \dots$，最终会进入一个环，并且再也出不来。

**证明**：只有 $n$ 个点，走 $n + 1$ 次一定有两次落在同一个点上（鸽巢原理），设 $f^i(x) = f^j(x)$，$i < j$。
从 $f^i(x)$ 往后走 $j - i$ 步又回到它自己，这就是一个环。每个点只有一条出边，走到环上以后下一步只能是环上的下一个点，出不去。$\blacksquare$

所以从 $x$ 出发的路径长得像希腊字母 ρ：先走一段「尾巴」，再绕圈。

```
a → b → c → d
        ↑   ↓
        f ← e          尾巴 a, b；环 c → d → e → f → c
```

### 2. 每个连通块恰好一个环

**引理 2**：把边当成无向的来看，每个连通块里**恰好一个环**，其余的点都在挂进环的树上。

**证明**：设一个连通块有 $k$ 个点。每个点一条出边，块里一共 $k$ 条边。
连通的 $k$ 个点至少要 $k - 1$ 条边（一棵生成树），树上再加 1 条边，正好产生 1 个环。
引理 1 说块里至少有一个有向环，那它就是唯一的那个。$\blacksquare$

整张图就是若干个「一个环 + 若干棵树，树根挂在环上的点」：

```
    x → y ↘
            c → d
    z → w ↗ ↑   ↓
            f ← e          树上的点：x, y, z, w；环上的点：c, d, e, f
```

几乎所有函数图题都是先把点分成**环上**和**树上**两类，再分开算。分的办法有两种，下面两节各讲一种。

> 题目允许 `edges[i] = -1`（没有出边）时，如 2360，图里还会多出「一棵树一路走到 -1 断掉」的连通块，里面没有环。下面的模板都兼容 -1。

### 3. 找所有环：时间戳

从每个没来过的点出发往下走，给走到的点**按顺序编号**（时间戳）。停下来只有三种情况：

| 停在哪 | 说明 | 怎么判断 |
|---|---|---|
| -1 | 走到头了，这一轮没环 | `node == -1` |
| 以前几轮走过的点 | 接上了旧路，环（如果有）早就算过了 | `first_seen[node] < round_begin` |
| **这一轮自己走过的点** | 自己绕回来了，发现一个新环 | `first_seen[node] >= round_begin` |

第三种情况下，环长 = 当前时钟 − 那个点的时间戳。每个点只被编号一次，总共 $O(n)$。

**为什么一定要比 `round_begin`，不能只看「来没来过」**：2360 的 `[3,3,4,2,3]`，第二轮从 1 出发，下一步就撞上第一轮走过的 3。
只看来没来过会把它当成新环，环长也会算错（时钟已经走到 6）。

### 4. 分开环和树：剥叶子（拓扑排序）

**做法**：数每个点的入度，把入度为 0 的点一个个剥掉（剥掉 $u$ 就让 $f(u)$ 的入度减 1），和 [Kahn 拓扑排序](../paradigms/bfs)（BFS 篇 §6）一模一样。**剥不掉的就是环上的点。**

**为什么**：
- 环上的点永远剥不掉：它的环上前驱也在环上，指向它的那条边永远不会被删，入度至少是 1。
- 树上的点一定剥得掉：树是有限的、无环的，从叶子开始一层层往环的方向剥，最后全剥光。

剥的过程中还能顺手做 DP：$\text{depth}[v]$ = 从树上走进 $v$ 的最长链有几个点。剥掉 $u$ 时，

$$
\text{depth}[f(u)] = \max\big(\text{depth}[f(u)],\ \text{depth}[u] + 1\big)
$$

$u$ 被剥的时候，所有走进 $u$ 的树上的点都已经剥完了，所以 $\text{depth}[u]$ 已经是终值。2127 要用这个数。

### 5. 走 $k$ 步，$k$ 到 $10^{10}$：倍增

一步一步走 $k$ 步太慢。和 [快速幂](./modular) 同一个想法：把 $k$ 拆成二进制，先预处理「从每个点走 $2^j$ 步到哪」：

$$
\text{jump}[0][i] = f(i), \qquad \text{jump}[j][i] = \text{jump}[j-1]\big[\text{jump}[j-1][i]\big]
$$

走 $2^j$ 步 = 先走 $2^{j-1}$ 步到 `mid`，再从 `mid` 走 $2^{j-1}$ 步。
要沿路累加点权时，同样再开一张 `total[j][i]`：$\text{total}[j][i] = \text{total}[j-1][i] + \text{total}[j-1][\text{mid}]$。

查询走 $k$ 步：$k$ 的第 $j$ 位是 1，就跳一次 $2^j$。预处理 $O(n \log k)$，每次查询 $O(\log k)$。

| | 快速幂 | 倍增 |
|---|---|---|
| 预处理的东西 | $x^{2^j}$ | 从每个点走 $2^j$ 步到哪 |
| 怎么从 $j-1$ 推到 $j$ | 平方 | 跳两次 $2^{j-1}$ |
| 查询 | $k$ 的第 $j$ 位是 1 就乘进去 | $k$ 的第 $j$ 位是 1 就跳过去 |

## 模板

::: code-group

```python [找所有环（时间戳）]
def find_cycles(nxt):
    """nxt[i] = i 指向的点, -1 表示没有出边。返回所有环, 每个环是一个点列表。"""
    n = len(nxt)
    first_seen = [0] * n          # 第几个时刻第一次走到这个点, 0 = 没来过
    clock = 1
    cycles = []
    for start in range(n):
        if first_seen[start]:
            continue
        round_begin = clock       # 这一轮从哪个时刻开始
        node = start
        while node != -1 and not first_seen[node]:
            first_seen[node] = clock
            clock += 1
            node = nxt[node]
        # 停下来了: 走到 -1, 或者撞上一个来过的点
        if node != -1 and first_seen[node] >= round_begin:
            # 撞上的是这一轮自己走过的点 -> 从 node 绕一圈就是新环
            cycle = [node]
            walker = nxt[node]
            while walker != node:
                cycle.append(walker)
                walker = nxt[walker]
            cycles.append(cycle)
    return cycles
```

```python [剥叶子（拓扑）]
from collections import deque

def peel(nxt):
    """返回 (on_cycle, order, depth):
    on_cycle[i]  i 在不在环上
    order        剥掉的树上的点, 按剥的先后
    depth[i]     从树上走进 i 的最长链有几个点(不含 i)"""
    n = len(nxt)
    indeg = [0] * n
    for u in range(n):
        if nxt[u] != -1:
            indeg[nxt[u]] += 1
    depth = [0] * n
    queue = deque(u for u in range(n) if indeg[u] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        v = nxt[u]
        if v == -1:
            continue
        depth[v] = max(depth[v], depth[u] + 1)
        indeg[v] -= 1
        if indeg[v] == 0:
            queue.append(v)
    on_cycle = [indeg[u] > 0 for u in range(n)]     # 剥不掉的就在环上
    return on_cycle, order, depth
```

```python [倍增]
def build_jump(nxt, steps):
    """jump[j][i]  = 从 i 走 2^j 步到哪
       total[j][i] = 这 2^j 步落脚的点的编号和(不含起点)"""
    levels = max(1, steps.bit_length())
    jump = [nxt[:]]
    total = [nxt[:]]                                 # 走 1 步, 落脚点就是 nxt[i]
    for j in range(1, levels):
        prev_jump, prev_total = jump[j - 1], total[j - 1]
        cur_jump, cur_total = [], []
        for i in range(len(nxt)):
            mid = prev_jump[i]                       # 先走 2^(j-1) 步到 mid
            cur_jump.append(prev_jump[mid])          # 再从 mid 走 2^(j-1) 步
            cur_total.append(prev_total[i] + prev_total[mid])
        jump.append(cur_jump)
        total.append(cur_total)
    return jump, total

def walk(jump, total, start, steps):
    """从 start 走 steps 步, 返回 (终点, 沿路落脚点编号和)。骨架和快速幂一样。"""
    node, acc = start, 0
    level = 0
    while steps:
        if steps & 1:                                # 这一位是 1: 跳 2^level 步
            acc += total[level][node]
            node = jump[level][node]
        steps >>= 1
        level += 1
    return node, acc
```

```python [验证]
import random

def brute_cycles(nxt):                       # 每个点暴力往下走 n+1 步找环
    found = set()
    for s in range(len(nxt)):
        node, path = s, []
        for _ in range(len(nxt) + 1):
            if node == -1:
                break
            if node in path:
                cyc = path[path.index(node):]
                i = cyc.index(min(cyc))
                found.add(tuple(cyc[i:] + cyc[:i]))     # 转成最小点打头, 方便比较
                break
            path.append(node)
            node = nxt[node]
    return found

def normalize(cycles):
    return {tuple(c[c.index(min(c)):] + c[:c.index(min(c))]) for c in cycles}

def brute_walk(nxt, start, steps):
    node, acc = start, 0
    for _ in range(steps):
        node = nxt[node]
        acc += node
    return node, acc

for _ in range(3000):
    n = random.randint(1, 9)
    nxt = [random.choice([-1] + [j for j in range(n) if j != i]) for i in range(n)]
    expect = brute_cycles(nxt)
    assert normalize(find_cycles(nxt)) == expect
    on_cycle, _, _ = peel(nxt)
    assert on_cycle == [any(i in c for c in expect) for i in range(n)]

for _ in range(2000):
    n = random.randint(1, 8)
    nxt = [random.randrange(n) for _ in range(n)]   # 倍增要求每个点都有出边
    steps = random.randint(1, 60)
    jump, total = build_jump(nxt, steps)
    for s in range(n):
        assert walk(jump, total, s, steps) == brute_walk(nxt, s, steps)
```

:::

## 例子

### 2360. Longest Cycle in a Graph：时间戳

最长环的长度，没有环返回 -1。`edges[i]` 可以是 -1。直接用时间戳模板，只留环长：

```python
class Solution:
    def longestCycle(self, edges: list[int]) -> int:
        n = len(edges)
        first_seen = [0] * n
        clock = 1
        best = -1
        for start in range(n):
            if first_seen[start]:
                continue
            round_begin = clock
            node = start
            while node != -1 and not first_seen[node]:
                first_seen[node] = clock
                clock += 1
                node = edges[node]
            if node != -1 and first_seen[node] >= round_begin:
                best = max(best, clock - first_seen[node])     # 环长 = 现在 - 第一次到它
        return best
```

手推 `edges = [3,3,4,2,3]`（答案 3）：

| 轮 | round_begin | 走过的点（时刻） | 停在 | first_seen[停点] | 判断 |
|---|---|---|---|---|---|
| 从 0 出发 | 1 | 0(1) → 3(2) → 2(3) → 4(4) | 3 | 2 ≥ 1 | 新环，长 5 − 2 = **3**（3 → 2 → 4） |
| 从 1 出发 | 5 | 1(5) | 3 | 2 < 5 | 撞上旧路，不算 |

2、3、4 第一轮已经编过号，后面直接跳过。

### 2876. Count Visited Nodes in a Directed Graph：剥叶子 + 倒序 DP

每个点出发能走到几个不同的点（含自己）。按引理 2 分两类：

- **环上的点**：绕一圈就回来了，答案 = 环长。
- **树上的点**：先走到下一个点，再接着它的答案，$\text{ans}[u] = \text{ans}[f(u)] + 1$。

树上的点要等 $f(u)$ 先算好。剥叶子的顺序里 $u$ 总在 $f(u)$ 前面（剥掉 $u$ 之后 $f(u)$ 才可能被剥），所以**倒着**处理剥的顺序就行：

```python
class Solution:
    def countVisitedNodes(self, edges: list[int]) -> list[int]:
        n = len(edges)
        on_cycle, order, _ = peel(edges)          # 模板
        ans = [0] * n
        for start in range(n):                    # 环上的点: 答案 = 环长
            if on_cycle[start] and ans[start] == 0:
                cycle = [start]
                walker = edges[start]
                while walker != start:
                    cycle.append(walker)
                    walker = edges[walker]
                for node in cycle:
                    ans[node] = len(cycle)
        for u in reversed(order):                 # 树上的点: 倒着剥的顺序, 下游先算好
            ans[u] = ans[edges[u]] + 1
        return ans
```

`edges = [1,2,0,0]`：剥掉的只有 3，环是 0 → 1 → 2。环上三个点答案都是 3，`ans[3] = ans[0] + 1 = 4`，输出 `[3,3,3,4]`。

### 2127. Maximum Employees to Be Invited to a Meeting：两种桌子

$n$ 个人，`favorite[i]` 是 $i$ 最喜欢的人。一张圆桌，每个人都要坐在 `favorite[i]` 旁边，最多能请几个人。

**先翻译成图**：$i \to \text{favorite}[i]$，每个点一条出边，是函数图。按环的大小，桌子只有两种坐法。

**情况 A：一个长度 ≥ 3 的环，整桌就是它。**
环 $c_1 \to c_2 \to \dots \to c_m \to c_1$ 上每个人都要挨着下一个人，这 $m$ 对「挨着」本身就围成一圈。
圆桌上的「挨着」关系也只有一个圈，所以桌上正好是这 $m$ 个人，**谁也插不进来**，也放不下第二个环。

**情况 B：长度 = 2 的环（互相喜欢），两边还能各接一条链。**
$a \leftrightarrow b$ 互相满足，坐一起。$a$ 外侧的座位可以给一条走进 $a$ 的链 $x_k \to \dots \to x_1 \to a$，每个人都挨着自己喜欢的下一个人；$b$ 那边同理：

```
x_k … x_2 x_1  a  b  y_1 y_2 … y_l
```

两端的 $x_k$、$y_l$ 外侧都空着，所以**好几段这样的东西可以首尾相接，围成一桌**。所有 2-环都能同时请。

$$
\text{答案} = \max\Big(\ \max_{\text{长度}\ge 3\ \text{的环}} |C|,\ \ \sum_{a \leftrightarrow b} \big(2 + \text{depth}[a] + \text{depth}[b]\big)\Big)
$$

$\text{depth}$ 就是剥叶子时顺手算的最长链。$b$ 在环上、不会被剥，所以 $\text{depth}[a]$ 里不会把 $b$ 算进去。

```python
class Solution:
    def maximumInvitations(self, favorite: list[int]) -> int:
        n = len(favorite)
        on_cycle, _, depth = peel(favorite)       # 模板
        biggest_ring = 0                          # 情况 A: 只能挑一个最大的
        pairs_total = 0                           # 情况 B: 全部加起来
        seen = [False] * n
        for start in range(n):
            if not on_cycle[start] or seen[start]:
                continue
            cycle = [start]
            seen[start] = True
            walker = favorite[start]
            while walker != start:
                cycle.append(walker)
                seen[walker] = True
                walker = favorite[walker]
            if len(cycle) == 2:
                a, b = cycle
                pairs_total += 2 + depth[a] + depth[b]
            else:
                biggest_ring = max(biggest_ring, len(cycle))
        return max(biggest_ring, pairs_total)
```

手推 `favorite = [2,2,1,2]`（答案 3）：1 ↔ 2 是 2-环；0 和 3 都指向 2。
剥掉 0、3，$\text{depth}[2] = 1$，$\text{depth}[1] = 0$，情况 B 得 $2 + 0 + 1 = 3$，坐法 `0 2 1`。
3 也喜欢 2，但 2 的两个座位已经给了 0 和 1，链在每一侧只能接一条，所以取的是最长的那条。

### 2836. Maximize Value of Function in a Ball Passing Game：倍增

从 $x$ 出发传 $k$ 次球，得分 = $x$ + 每次接球人的编号，$k \le 10^{10}$。求最大得分。

$k$ 太大不能模拟，直接套倍增模板，对每个起点查一次：

```python
class Solution:
    def getMaxFunctionValue(self, receiver: list[int], k: int) -> int:
        jump, total = build_jump(receiver, k)     # 模板
        best = 0
        for start in range(len(receiver)):
            _, acc = walk(jump, total, start, k)
            best = max(best, start + acc)
        return best
```

`receiver = [2,0,1]`，$k = 4 = 100_2$：

| $j$ | $\text{jump}[j]$ | $\text{total}[j]$ |
|---|---|---|
| 0 | [2, 0, 1] | [2, 0, 1] |
| 1 | [1, 2, 0] | [3, 2, 1] |
| 2 | [2, 0, 1] | [5, 3, 4] |

从 2 出发：$k$ 只有第 2 位是 1，跳一次 $2^2$ 步，累加 $\text{total}[2][2] = 4$（路径 2 → 1 → 0 → 2 → 1，落脚点和 1 + 0 + 2 + 1 = 4），得分 2 + 4 = **6**，就是答案。

复杂度 $O(n \log k)$，$\log_2 10^{10} \approx 34$ 层。

## 栽过的坑

只收自己真栽过的。

## 面试追问

::: details Q：函数图找环为什么不用三色 DFS？
也可以，但函数图每个点只有一条出边，「DFS」退化成一条直线往下走，不需要栈和回溯。
时间戳是三色的特化：「这一轮编的号」相当于灰色（在当前路径上），「以前几轮编的号」相当于黑色。
一般有向图的三色 DFS 见 [判环](./cycle-detection)。
:::

::: details Q：2127 为什么 2-环要全加起来，长环只取最大？
长环占满整张桌子，桌上不能再有别人，所以只能挑一个。2-环加上两条链是一条「线段」，两头空着，可以和别的线段首尾相接，所以能全请。两种不能混：有了长环就没有空座了。
:::

::: details Q：2836 不用倍增能做吗？
能。每个起点先走尾巴，进环以后 $k$ 步 = 若干整圈 + 余数，用环上的前缀和 $O(1)$ 算出整圈和余数段的和，总共 $O(n)$。
但要分「$k$ 走不出尾巴」「刚好进环」等情况，边界多。倍增不管图长什么样都是同一套，$O(n \log k)$ 也够快。
:::

::: details Q：倍增表为什么要求每个点都有出边？
`jump[j-1][mid]` 要求 `mid` 是合法下标。有 -1 的图（如 2360）要先特判：走到 -1 就停。2836 保证 `receiver[i]` 在 $[0, n)$ 里，可以直接用。
:::
