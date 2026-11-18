---
title: 建图：行和列当点
status: draft
order: 5
alias: []
related: [/paradigms/union-find, /structures/graph]
---

# 建图：行和列当点

> 题面里没有图时先问三件事：谁是点、谁是边、问的是连通还是先后；947 把行和列当点、石头当边，2392 把行和列拆成两张图各排一次序

## 一句话

题面里没有图，要自己决定谁是点、谁是边。定下来之后就落回 L3 的并查集 / 拓扑排序。

## 怎么认出这类题

题面是网格、石头、条件约束，问的却是「连通」「先后顺序」。

建在 L3 的：[并查集](../paradigms/union-find) · [图](../structures/graph)

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| **[947. Most Stones Removed with Same Row or Column](https://leetcode.com/problems/most-stones-removed-with-same-row-or-column/)** | 行列并查集 |
| [2392. Build a Matrix With Conditions](https://leetcode.com/problems/build-a-matrix-with-conditions/) | 行、列各做一次拓扑 |

## 原理

### 1. 建图三问

| | 947 | 2392 |
|---|---|---|
| 问的是什么 | 能删几块：哪些石头「连在一起」 | 怎么摆：谁在谁上面、谁在谁左边 |
| 落到哪个 L3 套路 | 连通 → [并查集](../paradigms/union-find) | 先后 → 拓扑排序（[BFS](../paradigms/bfs) 第 6 节） |
| 点 | **行和列**（不是石头） | 数字 1..k，行、列各一张图 |
| 边 | 一块石头 $(r, c)$ = 连接「第 $r$ 行」和「第 $c$ 列」的一条边 | 一个条件 `[a, b]` = 边 $a \to b$ |

先认出要问的是「连通」还是「先后」，套路就定了；剩下的难点全在「点和边怎么选」。

### 2. 947：答案 = 石头数 − 连通块数

**规则**：一块石头和**还在场上的**另一块同行或同列，就能删掉它。最多删几块？

把「同行或同列」当成边，石头分成若干个连通块。

**引理**：一个有 $k$ 块石头的连通块，最多删 $k - 1$ 块，而且能删到 $k - 1$ 块。

**证明**：

- **能删 $k - 1$ 块**：在这个块里取一棵生成树（比如 DFS 树），**从叶子往根删**。
  删一个非根的石头时，它在树上的父亲还在场，两者同行或同列，所以能删。最后剩下根。
- **删不光**：删石头不会让两块原本不同行也不同列的石头变成同行同列。
  不同连通块之间本来就没有同行同列的石头，所以一个块只剩最后一块时，场上没有谁和它同行同列，删不掉。$\blacksquare$

每个块都剩 1 块，所以

$$
\text{答案} = \text{石头数} - \text{连通块数}
$$

### 3. 947 为什么把行和列当点

直接按「石头两两之间同行同列就连边」建图要比较 $\binom{n}{2}$ 对。换个角度：**同行的石头之所以连通，是因为它们都碰到了同一行。**

把每一行、每一列都当成一个点，一块石头 $(r, c)$ 就是一条连接 $R_r$ 和 $C_c$ 的边：

```
石头: (0,0) (0,2) (1,1) (2,0) (2,2)

  R0 ── C0 ── R2          R1 ── C1
   │           │
   C2 ─────────┘
```

两块石头同行，它们的边就共用一个行点，所以在同一个连通块里。
所以**石头的连通块 ↔ 行列图里带边的连通块**，一一对应。每块石头只做一次 union，$O(n\,\alpha(n))$。

上图左边那块有 4 块石头，右边 1 块，答案 $5 - 2 = 3$。

**只数碰到过的点**：没有石头的行和列不算一个块。用 dict 当并查集，只有 `find` 过的行列才会进 `parent`，最后数不同的根就是块数。

### 4. 2392：行和列互不相干，各排一次

**规则**：把 1..k 放进 $k \times k$ 的矩阵，`rowConditions` 里 `[above, below]` 要求 above 所在行严格在 below 上面，`colConditions` 里 `[left, right]` 要求 left 所在列严格在 right 左边。

**观察**：行条件只管行号，列条件只管列号。给每个数**单独一行、单独一列**（$k$ 个数正好 $k$ 行 $k$ 列，放得下），两个方向就完全不相干了：

- 行号：把数字按 rowConditions 排一个先后顺序，第几个就放第几行。
- 列号：把数字按 colConditions 排一个先后顺序，第几个就放第几列。

每个方向都是「满足所有 $a$ 在 $b$ 前面」的一个排列，这正是**拓扑序**。

**无解 ⇔ 某个方向的条件有环**：有环就排不出先后（$a$ 在 $b$ 上面、$b$ 又在 $a$ 上面）；两边都无环，按上面的放法就一定满足所有条件。

## 模板

::: code-group

```python [并查集（dict 版，点可以是任何东西）]
parent = {}

def find(key):
    if key not in parent:                   # 第一次见到: 自己当根
        parent[key] = key
    while key != parent[key]:
        parent[key] = parent[parent[key]]   # 路径压缩: 挂到爷爷下面
        key = parent[key]
    return key

def union(a, b):
    root_a = find(a)
    root_b = find(b)
    if root_a != root_b:
        parent[root_b] = root_a             # 只动根

def count_components():
    return len({find(key) for key in parent})
```

```python [拓扑排序（Kahn）]
from collections import deque

def topo_order(k, conditions):
    """点是 1..k, [before, after] 表示 before 要排在 after 前面。有环返回 []。"""
    graph = [[] for _ in range(k + 1)]
    indeg = [0] * (k + 1)
    for before, after in conditions:
        graph[before].append(after)
        indeg[after] += 1
    queue = deque(x for x in range(1, k + 1) if indeg[x] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return order if len(order) == k else []     # 没排完 = 有环
```

```python [验证]
import random
from functools import lru_cache
from itertools import permutations

def brute_removed(stones):                      # 暴搜所有删除顺序
    @lru_cache(None)
    def go(left):
        best = 0
        for i, (r, c) in enumerate(left):
            others = left[:i] + left[i + 1:]
            if any(r == r2 or c == c2 for r2, c2 in others):
                best = max(best, 1 + go(others))
        return best
    return go(tuple(stones))

for _ in range(1000):
    cells = random.sample([(r, c) for r in range(4) for c in range(4)], random.randint(1, 7))
    parent.clear()
    for r, c in cells:
        union(('r', r), ('c', c))
    assert len(cells) - count_components() == brute_removed(tuple(cells))

for _ in range(2000):
    k = random.randint(2, 5)
    conds = [random.sample(range(1, k + 1), 2) for _ in range(random.randint(0, 6))]
    order = topo_order(k, conds)
    has_order = any(all(p.index(a) < p.index(b) for a, b in conds) for p in permutations(range(1, k + 1)))
    if has_order:
        assert sorted(order) == list(range(1, k + 1))
        assert all(order.index(a) < order.index(b) for a, b in conds)
    else:
        assert order == []
```

:::

## 例子

### 947. Most Stones Removed with Same Row or Column：行列并查集

```python
class Solution:
    def removeStones(self, stones: list[list[int]]) -> int:
        parent = {}                                 # 键: ('r', 行号) 或 ('c', 列号)

        def find(key):
            if key not in parent:
                parent[key] = key
            while key != parent[key]:
                parent[key] = parent[parent[key]]
                key = parent[key]
            return key

        for row, col in stones:                     # 一块石头 = 连接「它的行」和「它的列」的一条边
            root_row = find(('r', row))
            root_col = find(('c', col))
            if root_row != root_col:
                parent[root_col] = root_row

        components = len({find(key) for key in parent})
        return len(stones) - components
```

- **为什么键用 `('r', row)` 和 `('c', col)`**：行号和列号的取值范围重叠，第 0 行和第 0 列必须是两个不同的点。
  常见的另一种写法是列号加一个偏移（`col + 10001`），效果一样，元组更不容易写错。
- 手推上面那张图的例子：`[[0,0],[0,2],[1,1],[2,0],[2,2]]`，两个块，返回 $5 - 2 = 3$；
  `[[0,0],[0,1],[1,0],[1,2],[2,1],[2,2]]` 六块石头连成一块，返回 5。

### 2392. Build a Matrix With Conditions：两次拓扑

```python
class Solution:
    def buildMatrix(self, k: int, rowConditions: list[list[int]], colConditions: list[list[int]]) -> list[list[int]]:
        row_order = topo_order(k, rowConditions)    # 模板
        col_order = topo_order(k, colConditions)
        if not row_order or not col_order:          # 任一方向有环: 无解
            return []
        row_of = {num: idx for idx, num in enumerate(row_order)}
        col_of = {num: idx for idx, num in enumerate(col_order)}
        matrix = [[0] * k for _ in range(k)]
        for num in range(1, k + 1):
            matrix[row_of[num]][col_of[num]] = num
        return matrix
```

手推 `k = 3`，`rowConditions = [[1,2],[3,2]]`，`colConditions = [[2,1],[3,2]]`：

| | 条件 | 拓扑序 | 每个数的位置 |
|---|---|---|---|
| 行 | 1 在 2 上，3 在 2 上 | [1, 3, 2] | 1 → 第 0 行，3 → 第 1 行，2 → 第 2 行 |
| 列 | 2 在 1 左，3 在 2 左 | [3, 2, 1] | 3 → 第 0 列，2 → 第 1 列，1 → 第 2 列 |

```
[[0, 0, 1],
 [3, 0, 0],
 [0, 2, 0]]
```

题目接受任何合法答案，和官方样例长得不一样没关系。

## 栽过的坑

只收自己真栽过的。

## 面试追问

::: details Q：947 直接按石头两两连边行不行？
行。$n \le 1000$，$\binom{n}{2} \approx 5 \times 10^5$ 对，也能过。行列当点是 $O(n\,\alpha(n))$，而且不用想「两块石头什么时候连边」，一块石头就是一条边，更直接。
:::

::: details Q：947 为什么数连通块时不会把空行空列算进去？
dict 版并查集只有 `find` 过的键才会出现在 `parent` 里。每个键都是被某块石头碰到的行或列，所以每个连通块里至少有一块石头。
如果用数组版、提前把所有行列都初始化，就得只数「碰到过」的那些。
:::

::: details Q：2392 能不能让两个数共用一行？
可以共用，但没必要。给每个数单独一行一列，行列两个方向就完全分开了，各做一次拓扑排序就行；共用一行反而要同时照顾行和列的约束。
:::
