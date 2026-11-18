---
title: 铺砖 / 轮廓线 DP
status: draft
order: 7
alias: []
parent: bitmask-dp
related: [/paradigms/2d-dp]
---

# 铺砖 / 轮廓线 DP

> 网格 DP 为什么只需要记「交界线」；手推转移、按列压、逐格压三种写法分别什么时候用

## 一句话

网格有一维很小，就沿着另一维一列一列（或一格一格）推进，把交界处的状态压起来。

## 怎么认出这类题

铺砖、涂色这类网格题，其中一维 ≤ 5 左右。

- 另一维很长（$n \le 1000$，甚至 $10^9$）：一列一列推，长的那维变成 DP 的步数
- 约束只在**相邻格子**之间（相邻不同色、骨牌不重叠、邻居影响得分）

建在 L3 的：[状压 DP](./bitmask-dp) · [二维 DP](../paradigms/2d-dp)

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| [790. Domino and Tromino Tiling](https://leetcode.com/problems/domino-and-tromino-tiling/) | 先手推转移 |
| [1411. Number of Ways to Paint N × 3 Grid](https://leetcode.com/problems/number-of-ways-to-paint-n-3-grid/) | 先手推转移 |
| **[1931. Painting a Grid With Three Different Colors](https://leetcode.com/problems/painting-a-grid-with-three-different-colors/)** | 按列压状态 |
| [1659. Maximize Grid Happiness](https://leetcode.com/problems/maximize-grid-happiness/) | 逐格轮廓线 |

## 原理

### 1. 为什么只要记交界线

$5 \times 1000$ 的网格涂 3 种颜色，所有涂法有 $3^{5000}$ 种，不可能枚举。

但约束只在相邻格子之间：第 $j+1$ 列能怎么涂，**只看第 $j$ 列**，前面 $j-1$ 列怎么涂的无所谓。
所以把「前 $j$ 列」压成一个状态：**第 $j$ 列长什么样**。这条交界线就叫轮廓（profile）。

$$
\text{ways}[j][\text{col}] = \text{前 } j \text{ 列已经涂好、第 } j \text{ 列是 col 的方案数}
$$

$$
\text{ways}[j+1][\text{col}'] = \sum_{\text{col 和 col}' \text{ 能挨着}} \text{ways}[j][\text{col}]
$$

短的那维是 $m$，一列的状态最多 $3^m$ 种；$m \le 5$ 时 $3^5 = 243$，再去掉不合法的只剩 48 种。
**短的那维压成状态，长的那维变成 DP 的步数。**

按「状态有多少种」分三档写法：

| 状态数 | 写法 | 例子 |
|---|---|---|
| 两三种，能画出来 | 手推转移，几个标量滚动 | 790、1411 |
| 几十种 | 程序枚举所有合法列 + 兼容表 | 1931 |
| 一整列放不下，或者约束同时连上和左 | 逐格推进，轮廓是「最近 n 格」 | 1659 |

### 2. 逐格推进：轮廓是最近 n 格

1659 每个格子的得分取决于上边和左边的邻居。按行优先一格一格放，放到 $(r, c)$ 时：

- 正上方 $(r-1, c)$ 是 **n 格之前**放的
- 左边 $(r, c-1)$ 是 **上一格**放的

所以只要记**最近放的 n 格**。每格 3 种取值（空 / 内向 / 外向），把这 n 格当成一个 3 进制数，最老的在最高位：

```
          第 c 列
 . . . . [上]          ← 最近 n 格 = 轮廓
[左][当前] . .            最高位是「上」, 最低位是「左」
```

- 上：`profile // 3**(n-1)`（最高位）
- 左：`profile % 3`（最低位；$c = 0$ 时没有左邻居）
- 放完当前格，挤掉最老的一位：`nxt_profile = (profile * 3 + cur) % 3**n`

状态数是 $mn \cdot 3^n$ 再乘上题目里的其他计数维，每个状态只试 3 种放法。

### 3. 线性转移可以用矩阵快速幂

上面每一种转移都是「下一列的向量 = 固定矩阵 × 这一列的向量」。长的那维到 $10^{18}$ 时，
把转移写成矩阵 $M$，答案就是 $M^n$ 乘初值，见 [快速幂与取模](./modular) 的矩阵快速幂。
1931 的 $M$ 是 $48 \times 48$，$O(48^3 \log n)$。

## 模板

::: code-group

```python [按列压状态（1931）]
import itertools

def colorTheGrid(m: int, n: int) -> int:
    """m 行 n 列, 3 种颜色, 相邻格不同色。m <= 5。"""
    MOD = 10**9 + 7
    columns = []                                   # 一列内部合法: 上下相邻不同色
    for col in itertools.product(range(3), repeat=m):
        if all(col[r] != col[r + 1] for r in range(m - 1)):
            columns.append(col)
    k = len(columns)

    compat = [[] for _ in range(k)]                # compat[a]: 能接在 a 右边的列
    for a in range(k):
        for b in range(k):
            if all(columns[a][r] != columns[b][r] for r in range(m)):
                compat[a].append(b)

    ways = [1] * k                                 # 第一列: 每种合法列 1 种
    for _ in range(n - 1):
        nxt_ways = [0] * k
        for a in range(k):
            if ways[a] == 0:
                continue
            for b in compat[a]:
                nxt_ways[b] = (nxt_ways[b] + ways[a]) % MOD
        ways = nxt_ways
    return sum(ways) % MOD
```

```python [逐格轮廓线（1659）]
from functools import lru_cache

def getMaxGridHappiness(m: int, n: int, introvertsCount: int, extrovertsCount: int) -> int:
    BASE = [0, 120, 40]               # 0 空, 1 内向, 2 外向
    PAIR = [[0, 0, 0],                # PAIR[a][b]: a、b 相邻时两人幸福度变化之和
            [0, -60, -10],            # 内-内: -30-30; 内-外: -30+20
            [0, -10, 40]]             # 外-外: +20+20
    top_unit = 3 ** (n - 1)           # 轮廓最高位 = 正上方那格
    all_units = 3 ** n

    @lru_cache(maxsize=None)
    def dfs(pos, profile, intro_left, extro_left):
        if pos == m * n:
            return 0
        col = pos % n
        up = profile // top_unit
        left = profile % 3 if col > 0 else 0
        best = 0
        for cur in range(3):
            if cur == 1 and intro_left == 0:
                continue
            if cur == 2 and extro_left == 0:
                continue
            gain = BASE[cur] + PAIR[cur][up] + PAIR[cur][left]
            nxt_profile = (profile * 3 + cur) % all_units   # 挤掉最老的一位
            nxt_intro = intro_left - (cur == 1)
            nxt_extro = extro_left - (cur == 2)
            cand = gain + dfs(pos + 1, nxt_profile, nxt_intro, nxt_extro)
            if cand > best:
                best = cand
        return best

    return dfs(0, 0, introvertsCount, extrovertsCount)
```

```python [验证]
import itertools, random

def raw_color(m, n):                  # 暴力: 枚举整张网格
    cnt = 0
    for g in itertools.product(range(3), repeat=m * n):
        ok = all(not (r + 1 < m and g[(r + 1) * n + c] == g[r * n + c]) and
                 not (c + 1 < n and g[r * n + c + 1] == g[r * n + c])
                 for r in range(m) for c in range(n))
        cnt += ok
    return cnt

for m in range(1, 4):
    for n in range(1, 5):
        if m * n <= 10:
            assert colorTheGrid(m, n) == raw_color(m, n)
assert colorTheGrid(1, 1) == 3 and colorTheGrid(1, 2) == 6 and colorTheGrid(5, 5) == 580986

def raw_happy(m, n, I, E):            # 暴力: 枚举每格放什么
    best = 0
    for g in itertools.product(range(3), repeat=m * n):
        if g.count(1) > I or g.count(2) > E:
            continue
        score = 0
        for r in range(m):
            for c in range(n):
                v = g[r * n + c]
                if v == 0:
                    continue
                score += 120 if v == 1 else 40
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < m and 0 <= cc < n and g[rr * n + cc]:
                        score += -30 if v == 1 else 20
        best = max(best, score)
    return best

assert getMaxGridHappiness(2, 3, 1, 2) == 240
assert getMaxGridHappiness(3, 1, 2, 1) == 260
assert getMaxGridHappiness(2, 2, 4, 0) == 240
for _ in range(100):
    m, n = random.randrange(1, 4), random.randrange(1, 4)
    if m * n <= 8:
        I, E = random.randrange(5), random.randrange(5)
        assert getMaxGridHappiness(m, n, I, E) == raw_happy(m, n, I, E)
```

:::

## 例子

### 790. Domino and Tromino Tiling：手推两个状态

$2 \times n$ 的板，用 $1 \times 2$ 骨牌和 L 形三格骨牌铺满，问方案数。

只看右边界，铺到一半的形状只有两种（上下翻转算同一种）：

```
full[i]: 前 i 列铺满            part[i]: 前 i 列铺满, 第 i+1 列只多了上面一格
█ █ █ █                          █ █ █ █ █
█ █ █ █                          █ █ █ █ .
```

**full[i] 怎么来**：看是谁盖住了第 $i$ 列的两格：

```
① 竖骨牌           ② 两根横骨牌         ③ L 形盖住第 i 列两格 + 第 i-1 列一格
. . . A            . . B B              . . . C C        . . . . C
. . . A            . . D D              . . . . C        . . . C C
→ full[i-1]        → full[i-2]          → part[i-2]，上下两种朝向 ×2
```

**part[i] 怎么来**：看是谁盖住了多出来的那一格 $(上, i+1)$：

```
① 横骨牌盖住 (上,i)(上,i+1)        ② L 形盖住 (上,i+1)(上,i)(下,i)
. . . A A                          . . . C C
. . . .                            . . . C
→ 剩下 i-1 列 + (下,i) 一格         → 剩下 i-1 列铺满
→ part[i-1]（翻转）                 → full[i-1]
```

$$
\text{full}[i] = \text{full}[i-1] + \text{full}[i-2] + 2 \cdot \text{part}[i-2], \qquad
\text{part}[i] = \text{part}[i-1] + \text{full}[i-1]
$$

初值 $\text{full}[0] = 1$（空板一种铺法），$\text{part}[0] = 0$（单独一格铺不了）。

| i | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| full | 1 | 1 | 2 | 5 | 11 | 24 |
| part | 0 | 1 | 2 | 4 | 9 | 20 |

```python
class Solution:
    def numTilings(self, n: int) -> int:
        MOD = 10**9 + 7
        full = [0] * (n + 1)
        part = [0] * (n + 1)
        full[0] = 1
        for i in range(1, n + 1):
            full[i] = full[i - 1]
            if i >= 2:
                full[i] += full[i - 2] + 2 * part[i - 2]
            part[i] = part[i - 1] + full[i - 1]
            full[i] %= MOD
            part[i] %= MOD
        return full[n]
```

和暴力铺砖对拍过 $n \le 10$。消掉 part 还能化成一条 $\text{full}[i] = 2\,\text{full}[i-1] + \text{full}[i-3]$（$24 = 2 \cdot 11 + 2$），但两个状态的版本更好推。

### 1411. Number of Ways to Paint N × 3 Grid：按「形状」分两类

$n \times 3$，3 种颜色，相邻不同色。一行合法的涂法有 12 种，分成两类：

- **ABA 型**（两头同色）：$3 \times 2 = 6$ 种，如 `010`
- **ABC 型**（三格都不同）：$3! = 6$ 种，如 `012`

同一类里的行，往下接的方式数一样（换个颜色名字而已）。手数一下下一行能接什么：

- `010` 下面：`101 121 202`（ABA）、`102 201`（ABC）→ **3 个 ABA + 2 个 ABC**
- `012` 下面：`101 121`（ABA）、`120 201`（ABC）→ **2 个 ABA + 2 个 ABC**

$$
\text{aba}' = 3\,\text{aba} + 2\,\text{abc}, \qquad \text{abc}' = 2\,\text{aba} + 2\,\text{abc}
$$

| 行数 | aba | abc | 总数 |
|---|---|---|---|
| 1 | 6 | 6 | 12 |
| 2 | 30 | 24 | 54 |
| 3 | 138 | 108 | 246 |

```python
class Solution:
    def numOfWays(self, n: int) -> int:
        MOD = 10**9 + 7
        aba, abc = 6, 6
        for _ in range(n - 1):
            nxt_aba = (3 * aba + 2 * abc) % MOD
            nxt_abc = (2 * aba + 2 * abc) % MOD
            aba, abc = nxt_aba, nxt_abc
        return (aba + abc) % MOD
```

`nxt_aba`、`nxt_abc` 都用旧值算完再一起赋回去，别先改 `aba` 再用它算 `abc`。

### 1931. Painting a Grid With Three Different Colors：让程序去数

1411 是 $m = 3$ 的特例（`colorTheGrid(3, n)` 和 1411 的答案一样）。$m$ 到 5 时手推不动了，交给程序枚举，代码就是上面的模板。

拿 $m = 2$ 看一下它在数什么。合法的列（上下不同色）有 6 种，每种能接 3 种：

| 列 | 能接在右边的列 |
|---|---|
| `01` | `10` `12` `20` |
| `02` | `10` `20` `21` |
| `10` | `01` `02` `21` |
| `12` | `01` `20` `21` |
| `20` | `01` `02` `12` |
| `21` | `02` `10` `12` |

所以 $2 \times n$ 的答案是 $6 \cdot 3^{n-1}$：$n = 2$ 时 18。

不同 $m$ 的规模：

| m | 合法列数 $3 \cdot 2^{m-1}$ | 兼容对数 |
|---|---|---|
| 3 | 12 | 54 |
| 4 | 24 | 162 |
| 5 | 48 | 486 |

$n = 1000$ 时总共约 $486 \times 1000 \approx 5 \times 10^5$ 次加法。

### 1659. Maximize Grid Happiness：逐格轮廓线

$m, n \le 5$，内向的人最多 6 个、外向的人最多 6 个，放进网格，最大化总幸福度。代码就是上面的模板。

**状态**：(第几格, 最近 n 格的轮廓, 还剩几个内向, 还剩几个外向)。
**规模**：$25 \times 3^5 \times 7 \times 7 \approx 3 \times 10^5$ 个状态，每个试 3 种。

**相邻得分为什么能拆成 PAIR 表**：两个人相邻，两人各自的变化加起来只取决于这两人的类型。
所以放当前格时，把它和上、左两个邻居之间的**两人份**变化一次算清，以后放右边、下边的格时再算它们那一对，不会重复也不会漏。

**轮廓手推**：$n = 3$，第 0 行放了 `内 空 外`（`1 0 2`），轮廓 $= 1 \cdot 9 + 0 \cdot 3 + 2 = 11$。

| 放到 | 轮廓（3 进制） | 上 = 最高位 | 左 = 最低位 |
|---|---|---|---|
| (1, 0) | `102` = 11 | 1（内向） | 没有（第 0 列） |
| 放了外向后 → (1, 1) | `(11·3 + 2) % 27 = 8` = `022` | 0（空） | 2（外向） |

$(1, 1)$ 的正上方是 $(0, 1)$，确实是空的；左边 $(1, 0)$ 刚放了外向。对上了。

## 栽过的坑

只收自己真栽过的。

## 面试追问

::: details Q：1931 为什么按列压，不按行压？
$m \le 5$ 是短边，$n \le 1000$ 是长边。按短边压，一列只有 48 种；按长边压，一行是 1000 格，状态爆炸。
**永远压短的那一维。**
:::

::: details Q：按列压和逐格压怎么选？
按列压：一步要枚举「上一列 × 下一列」两两组合，$k^2$。逐格压：一步只决定一格，状态是 $3^n$，每步只试 3 种。
列状态少（1931 的 48）就按列压，好写；列状态多、或者约束同时牵扯上和左（1659），逐格压更省。
:::

::: details Q：n 到 10^18 怎么办？
转移是线性的：下一列的计数向量 = 固定矩阵 × 这一列的向量。用 [矩阵快速幂](./modular)，$O(k^3 \log n)$，$k$ 是状态数。
1411 只有 2 个状态，就是一个 $2 \times 2$ 矩阵 $\begin{pmatrix} 3 & 2 \\ 2 & 2 \end{pmatrix}$ 的幂。
:::
