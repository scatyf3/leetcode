---
title: 判环
status: draft
order: 4
alias: []
related: [/paradigms/dfs, /paradigms/bfs, /structures/graph]
---

# 判环

> 有向图用三色 DFS 或拓扑排序，无向图用并查集；「最短的环」要从每个点 BFS 一遍，为什么非树边给的长度不会偏小

## 一句话

有向图、无向图、网格，判环的办法各不相同；问「最短的环」又是另一回事。

## 怎么认出这类题

问「是否存在环」「最短的环有多长」「哪些点永远不会走进环」。

建在 L3 的：[DFS](../paradigms/dfs) · [BFS](../paradigms/bfs) · [图](../structures/graph)

在 [图的形状](./graph-shapes) 的思维导图里，这一页讲的是一般有向图、一般无向图和基环树三片叶子；出度 ≤ 1 的图走 [函数图](./functional-graph)。

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| **[802. Find Eventual Safe States](https://leetcode.com/problems/find-eventual-safe-states/)** | 反向拓扑 |
| [2608. Shortest Cycle in a Graph](https://leetcode.com/problems/shortest-cycle-in-a-graph/) | 无向图最短环，用 BFS |
| [1559. Detect Cycles in 2D Grid](https://leetcode.com/problems/detect-cycles-in-2d-grid/) | 网格判环 |

## 原理

先分清三种问法，用的东西不一样：

| 问法 | 图 | 用什么 |
|---|---|---|
| 有没有环 | 有向 | 三色 DFS，或 Kahn 拓扑排序看能不能排完 |
| 有没有环 | 无向 / 网格 | 并查集：加边前两端已经连通 → 成环 |
| 哪些点走不进环 | 有向 | 反向图上做拓扑（802） |
| 最短的环多长 | 无向 | 从每个点 BFS，看非树边（2608） |

### 1. 有向图：三色 DFS

为什么一个 visited 不够、要三种状态，L3 已经讲过，见 [图](../structures/graph) 第 3 节。这里补上**为什么它对**。

- 白：没碰过
- 灰：进了 DFS、还没出来，**就是当前递归栈上的那条路径**
- 黑：出来了，从它能走到的点全部处理完

**引理 1**：有向图有环 ⇔ DFS 过程中有某条边 $u \to v$ 指向一个灰点 $v$。

**证明**：

- ⇐：灰点都在当前路径上，$v$ 是 $u$ 的祖先，路径上有 $v \to \dots \to u$，再加上 $u \to v$，就是一个环。
- ⇒：设图里有环 $C$，$v$ 是 $C$ 上**第一个**变灰的点。那一刻 $C$ 上其他点都还是白的。
  DFS 从 $v$ 出发，沿着白点能走到的都会在 $v$ 变黑之前处理掉，包括 $C$ 上 $v$ 的前一个点 $u$。
  处理 $u$ 时，看到的边 $u \to v$ 指向的 $v$ 还是灰的。$\blacksquare$

**另一种写法**：Kahn 拓扑排序，排出来的点数 < $n$ 就有环，见 [BFS](../paradigms/bfs) 第 6 节。两种写法判的是同一件事，挑顺手的。

> $n$ 到 $10^5$ 时递归版会爆 Python 的栈（默认 1000 层），下面的模板用显式栈写。

### 2. 哪些点走不进环：反向拓扑（802）

802 的「安全点」：从它出发，不管怎么走，最后都停在终点（没有出边的点）。

**等价说法**：安全 ⇔ 从它出发走不到任何环。
（有限图里一条路走不停，一定会重复经过某个点，也就是在绕环。）

**递推**：终点是安全的；一个点安全 ⇔ 它的**所有**出边邻居都安全。

这个「所有邻居都确认了才轮到我」，就是 Kahn 的 AND 规则，只是方向反过来：

| | Kahn（207） | 802 |
|---|---|---|
| 等什么 | 所有**前置**修完 | 所有**出边邻居**确认安全 |
| 计数器 | 入度 `indeg[v]` | 出度 `out_left[u]` |
| 起点 | 入度 0 的点 | 出度 0 的点（终点） |
| 确认了 $v$ 以后通知谁 | $v$ 的出边邻居 | 指向 $v$ 的点，所以要建**反向图** |

环上的点、以及能走进环的点，总有一条出边通往不安全的地方，`out_left` 永远减不到 0，永远进不了队。

### 3. 无向图最短环：从每个点 BFS（2608）

**做法**：从每个点 $s$ 做一次 BFS，记下 $\text{dist}$ 和 $\text{parent}$。
看到一条边 $u - v$，$v$ 已经访问过、又不是 $u$ 的父亲（也就是**非树边**），就得到一个候选：

$$
\text{dist}[u] + \text{dist}[v] + 1
$$

所有起点、所有候选取最小。复杂度 $O(n(n + m))$，2608 里 $n, m \le 1000$。

**为什么对**：要证两件事，候选不会比最短环 $g$ 小，而且一定有某个候选恰好是 $g$。

**(a) 候选不会偏小。** $s \leadsto u$、边 $u - v$、$v \leadsto s$ 拼成一个长度为候选值的闭合路线。
两条树路径从 $s$ 出发，先共用一段，到某个分叉点 $w$ 后分开；去掉共用那段，剩下 $w \leadsto u - v \leadsto w$ 是一个真正的环，长度 ≤ 候选值。
所以每个候选 ≥ 某个环的长度 ≥ $g$。

**(b) 有一个候选恰好是 $g$。** 取 $s$ 在某个最短环 $C$ 上。

先说一个事实：**最短环上两点的图距离，就等于沿环走的距离**。
否则在图里抄一条更短的近路，近路加上环上较短的那段弧，能拼出一个比 $C$ 还短的环，矛盾。

所以 BFS 给 $C$ 上各点的 $\text{dist}$，就是它们沿环到 $s$ 的距离：

- $g$ 是奇数：环上离 $s$ 最远的是一条边 $u - v$，两端的 $\text{dist}$ 都是 $\frac{g-1}{2}$。
  树边只连相邻两层，同一层之间的边一定是非树边，候选 $= \frac{g-1}{2} \cdot 2 + 1 = g$。
- $g$ 是偶数：离 $s$ 最远的是一个点 $w$，$\text{dist}[w] = \frac{g}{2}$，它在环上的两个邻居都在 $\frac{g}{2} - 1$ 层。
  $w$ 只有一个父亲，另一条边是非树边，候选 $= (\frac{g}{2} - 1) + \frac{g}{2} + 1 = g$。$\blacksquare$

**单个起点的候选可能偏大**，这就是为什么要从每个点都 BFS 一遍。三角形 0-1-2 挂一条尾巴 3-0：

| 起点 | dist | 非树边给的候选 |
|---|---|---|
| 0 | [0, 1, 1, 1] | 3 |
| 3 | [1, 2, 2, 0] | **5**：3 → 0 → 1 → 2 → 0 → 3，0 走了两次，不是简单环 |

起点不在最短环上，拼出来的路线会带上一段来回走的尾巴。(a) 保证它不会比 $g$ 小，(b) 保证在环上的起点能拿到 $g$。

### 4. 无向图 / 网格判环：并查集

和 [并查集](../paradigms/union-find) 里 684 一样：边一条条加，**加之前两端已经同根，这条边就把环闭上了**。
不用管方向，也不用管父节点，网格题尤其顺手（1559）。

## 模板

::: code-group

```python [有向图：三色 DFS（迭代）]
WHITE, GRAY, BLACK = 0, 1, 2

def has_cycle_directed(n, graph):
    """graph[u] = u 的出边邻居列表。显式栈, 不怕递归深度。"""
    color = [WHITE] * n
    for root in range(n):
        if color[root] != WHITE:
            continue
        color[root] = GRAY
        stack = [(root, 0)]                 # (点, 下一个要看的邻居下标)
        while stack:
            u, idx = stack[-1]
            if idx == len(graph[u]):        # 邻居都看完了: 出栈, 变黑
                color[u] = BLACK
                stack.pop()
                continue
            stack[-1] = (u, idx + 1)        # 先把下标往后挪, 再处理这个邻居
            v = graph[u][idx]
            if color[v] == GRAY:            # 指回当前路径上的点: 环
                return True
            if color[v] == WHITE:
                color[v] = GRAY
                stack.append((v, 0))
    return False
```

```python [无向图：并查集判环]
def has_cycle_undirected(n, edges):
    parent = list(range(n))

    def find(idx):
        while idx != parent[idx]:
            parent[idx] = parent[parent[idx]]     # 路径压缩
            idx = parent[idx]
        return idx

    for u, v in edges:
        root_u = find(u)
        root_v = find(v)
        if root_u == root_v:                      # 两端早就连通: 这条边闭上了一个环
            return True
        parent[root_v] = root_u                   # 只动根
    return False
```

```python [无向图：最短环]
from collections import deque

def shortest_cycle(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    best = float('inf')
    for source in range(n):
        dist = [-1] * n
        parent = [-1] * n
        dist[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if dist[v] == -1:           # 第一次见: 树边
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif v != parent[u]:        # 见过、又不是来的那条边: 非树边
                    best = min(best, dist[u] + dist[v] + 1)
    return -1 if best == float('inf') else best
```

```python [验证]
import random
from itertools import combinations, permutations

def reaches_itself(graph, s):                    # 从 s 出发走 >= 1 步能不能回到 s
    seen, todo = set(), list(graph[s])
    while todo:
        x = todo.pop()
        if x == s:
            return True
        if x not in seen:
            seen.add(x)
            todo.extend(graph[x])
    return False

def brute_girth(n, edges):                       # 枚举所有点的排列, 找最短的环
    edge_set = {frozenset(e) for e in edges}
    for length in range(3, n + 1):
        for nodes in combinations(range(n), length):
            for rest in permutations(nodes[1:]):
                cyc = (nodes[0],) + rest
                if all(frozenset((cyc[i], cyc[(i + 1) % length])) in edge_set for i in range(length)):
                    return length
    return -1

for _ in range(3000):
    n = random.randint(1, 8)
    graph = [random.sample(range(n), random.randint(0, min(3, n))) for _ in range(n)]
    assert has_cycle_directed(n, graph) == any(reaches_itself(graph, s) for s in range(n))

for _ in range(1500):
    n = random.randint(2, 7)
    pairs = list(combinations(range(n), 2))
    edges = random.sample(pairs, random.randint(1, len(pairs)))
    girth = brute_girth(n, edges)
    assert shortest_cycle(n, edges) == girth
    assert has_cycle_undirected(n, edges) == (girth != -1)

chain = [[i + 1] for i in range(99999)] + [[]]   # 10^5 个点的长链, 递归版会爆栈
assert not has_cycle_directed(100000, chain)
```

:::

## 例子

### 802. Find Eventual Safe States：反向拓扑

返回所有安全点，升序。按原理第 2 节：建反向图，出度当计数器，从终点开始往回确认。

```python
from collections import deque

class Solution:
    def eventualSafeNodes(self, graph: list[list[int]]) -> list[int]:
        n = len(graph)
        reverse = [[] for _ in range(n)]        # reverse[v] = 哪些点有边指向 v
        out_left = [0] * n                      # 还有几条出边没确认安全
        for u in range(n):
            out_left[u] = len(graph[u])
            for v in graph[u]:
                reverse[v].append(u)
        queue = deque(u for u in range(n) if out_left[u] == 0)   # 终点: 没有出边
        safe = [False] * n
        while queue:
            v = queue.popleft()
            safe[v] = True
            for u in reverse[v]:                # u -> v 这条边确认安全了
                out_left[u] -= 1
                if out_left[u] == 0:            # u 的出边全安全, u 也安全
                    queue.append(u)
        return [u for u in range(n) if safe[u]]
```

手推 `graph = [[1,2],[2,3],[5],[0],[5],[],[]]`（答案 `[2,4,5,6]`）：

```
0 → 1 → 3 → 0        环
0 → 2 → 5            2、5 安全
1 → 2,  4 → 5        6 孤立
```

| 出队 | 通知谁 | 结果 |
|---|---|---|
| 5 | 2、4 的 `out_left` 各减 1 | 2：1 → 0，入队；4：1 → 0，入队 |
| 6 | 没人指向它 | |
| 2 | 0、1 各减 1 | 0：2 → 1；1：2 → 1 |
| 4 | 没人指向它 | |

结束时 `out_left = [1,1,0,1,0,0,0]`。0、1、3 各有一条出边在环里，永远减不到 0。

**三色 DFS 也能做**：安全点就是 DFS 结束时变黑、而且从它出发没碰到灰点的点。反向拓扑不用递归，也不用想「中途发现环以后怎么标记」，更直接。

### 2608. Shortest Cycle in a Graph：每个点 BFS

最短环的长度，没有环返回 -1。直接套模板：

```python
from collections import deque

class Solution:
    def findShortestCycle(self, n: int, edges: list[list[int]]) -> int:
        graph = [[] for _ in range(n)]
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)
        best = float('inf')
        for source in range(n):
            dist = [-1] * n
            parent = [-1] * n
            dist[source] = 0
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for v in graph[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        parent[v] = u
                        queue.append(v)
                    elif v != parent[u]:
                        best = min(best, dist[u] + dist[v] + 1)
        return -1 if best == float('inf') else best
```

- **为什么判 `v != parent[u]`**：无向边两头都存了，$u$ 一定会看到来时那条边，它不是环。2608 保证没有重边，所以「是父亲」就等于「是来时那条边」。
- **为什么不能 BFS 一次就停**：见原理第 3 节的表，起点不在最短环上时候选会偏大。

### 1559. Detect Cycles in 2D Grid：网格判环

同一个字母的相邻格子连边，问有没有环（题目要求长度 ≥ 4）。
网格里没有三角形（相邻格子的行号加列号奇偶相反，不可能三个两两相邻），来回走一条边又被「不走回父格」挡掉，所以**只要有环，长度自动 ≥ 4**。

::: code-group

```python [并查集]
class Solution:
    def containsCycle(self, grid: list[list[str]]) -> bool:
        rows, cols = len(grid), len(grid[0])
        parent = list(range(rows * cols))       # 格子 (r, c) 编号成 r * cols + c

        def find(idx):
            while idx != parent[idx]:
                parent[idx] = parent[parent[idx]]
                idx = parent[idx]
            return idx

        for r in range(rows):
            for c in range(cols):
                here = r * cols + c
                for nr, nc in ((r, c + 1), (r + 1, c)):     # 每条边只看一次: 右和下
                    if nr < rows and nc < cols and grid[nr][nc] == grid[r][c]:
                        root_here = find(here)
                        root_there = find(nr * cols + nc)
                        if root_here == root_there:         # 早就连通, 再连就成环
                            return True
                        parent[root_there] = root_here
        return False
```

```python [DFS + 父格]
class Solution:
    def containsCycle(self, grid: list[list[str]]) -> bool:
        rows, cols = len(grid), len(grid[0])
        seen = [[False] * cols for _ in range(rows)]
        for sr in range(rows):
            for sc in range(cols):
                if seen[sr][sc]:
                    continue
                seen[sr][sc] = True
                stack = [(sr, sc, -1, -1)]      # (格子, 从哪个格子来)
                while stack:
                    r, c, pr, pc = stack.pop()
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                        if not (0 <= nr < rows and 0 <= nc < cols):
                            continue
                        if grid[nr][nc] != grid[r][c] or (nr, nc) == (pr, pc):
                            continue
                        if seen[nr][nc]:        # 同色、来过、又不是父格: 环
                            return True
                        seen[nr][nc] = True
                        stack.append((nr, nc, r, c))
        return False
```

:::

并查集版只看右和下，每条边处理一次，不用记父格。DFS 版要记父格，否则一走出去就看到来时的格子，误判成环。
DFS 版里「来过」可以是入栈时标的，而不是出栈时，因为无向图里任何一条连到已标记格子的非父边都闭上了一个环（和有向图不同，不需要区分灰和黑）。

## 栽过的坑

只收自己真栽过的。

## 面试追问

::: details Q：无向图判环能用三色 DFS 吗？
不需要三色。无向图里任何一条通往已访问点、又不是来时那条边的边，都闭上一个环，「来过没有」加「父节点」就够了。
三色是给有向图用的：有向图里指向黑点的边（比如 `0→1→2、0→2` 里的 `0→2`）不构成环，必须区分灰和黑。
:::

::: details Q：有向图的最短环怎么求？
从每个点 $s$ BFS，第一次看到一条指回 $s$ 的边 $u \to s$ 时，$\text{dist}[u] + 1$ 就是过 $s$ 的最短环。所有 $s$ 取最小，$O(n(n + m))$。
有向图里没有「来时那条边」的问题，但只有指回起点的边才算，不能套无向图的 $\text{dist}[u] + \text{dist}[v] + 1$。
:::

::: details Q：2608 的边带权怎么办？
对每条边 $(u, v, w)$：先把它删掉，用 Dijkstra 求 $u$ 到 $v$ 的最短路 $d$，候选是 $d + w$，所有边取最小。
经过这条边的最短环，就是这条边加上「不走这条边的 $u \to v$ 最短路」。$O(m \cdot m \log n)$。
:::

::: details Q：802 为什么不直接从每个点 DFS 看会不会走进环？
每个点单独 DFS 是 $O(n(n + m))$。反向拓扑每条边只处理一次，$O(n + m)$。三色 DFS 记住结果也能做到 $O(n + m)$。
:::
