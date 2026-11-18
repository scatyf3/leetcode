---
title: 组合计数
status: draft
order: 2
alias: []
related: [/paradigms/1d-dp, /advanced/modular]
---

# 组合计数

> $C(n, k)$ 是什么、取模下怎么算；隔板法和容斥怎么把「分东西」的方案数直接算出来；Catalan 数和第一类斯特林数从哪来

## 一句话

不把方案一个个列出来，用组合数、隔板法、容斥直接把方案数算出来。

## 怎么认出这类题

问「有多少种方式」并且要取模；n 大到 DP 都嫌慢，或者 DP 的转移式能化成 C(n, k)。

建在 L3 的：[一维 DP](../paradigms/1d-dp)（计数 DP）· [快速幂与取模](./modular)（组合数要用逆元）

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| **[2400. Number of Ways to Reach a Position After Exactly k Steps](https://leetcode.com/problems/number-of-ways-to-reach-a-position-after-exactly-k-steps/)** · [tracker](https://github.com/scatyf3/leetcode/tree/main/tracker/2400.%20Number%20of%20Ways%20to%20Reach%20a%20Position%20After%20Exactly%20k%20Steps) | 组合数取模模板 |
| [2929. Distribute Candies Among Children II](https://leetcode.com/problems/distribute-candies-among-children-ii/) | 隔板法 + 容斥 |
| [1866. Number of Ways to Rearrange Sticks With K Sticks Visible](https://leetcode.com/problems/number-of-ways-to-rearrange-sticks-with-k-sticks-visible/) | 第一类斯特林数 |
| [1569. Number of Ways to Reorder Array to Get Same BST](https://leetcode.com/problems/number-of-ways-to-reorder-array-to-get-same-bst/) | 递归里套组合数 |
| [1916. Count Ways to Build Rooms in an Ant Colony](https://leetcode.com/problems/count-ways-to-build-rooms-in-an-ant-colony/) | 树上的拓扑序计数 |
| [1259. Handshakes That Don't Cross](https://leetcode.com/problems/handshakes-that-dont-cross/) | Catalan 数（会员题） |
| [2338. Count the Number of Ideal Arrays](https://leetcode.com/problems/count-the-number-of-ideal-arrays/) | 附加题：隔板法 + 质因数分解 |

## 原理

### 1. 组合数 $C(n, k)$

**定义**：从 $n$ 个不同的东西里**挑出** $k$ 个，不管顺序，有几种挑法。

$$
C(n, k) = \binom{n}{k} = \frac{n!}{k!\,(n-k)!}
$$

**为什么是这个式子**：先按顺序挑，第一个有 $n$ 种、第二个 $n-1$ 种……一共 $n(n-1)\cdots(n-k+1) = \dfrac{n!}{(n-k)!}$ 种。
同一组 $k$ 个东西被按 $k!$ 种顺序各数了一遍，除掉就是不计顺序的挑法数。

例：$C(4, 2) = 6$，从 $\{a, b, c, d\}$ 挑两个：$ab, ac, ad, bc, bd, cd$。

**对称**：$C(n, k) = C(n, n-k)$。挑出 $k$ 个，等于挑出不要的 $n-k$ 个。

### 2. 杨辉三角递推

$$
C(n, k) = C(n-1, k-1) + C(n-1, k), \qquad C(n, 0) = C(n, n) = 1
$$

**为什么**：盯住第 $n$ 个东西。挑法分成两种，互不重叠：

- 挑了它：剩下 $k-1$ 个从前 $n-1$ 个里挑，$C(n-1, k-1)$ 种
- 没挑它：$k$ 个全从前 $n-1$ 个里挑，$C(n-1, k)$ 种

| n | C(n, 0..n) |
|---|---|
| 0 | 1 |
| 1 | 1 1 |
| 2 | 1 2 1 |
| 3 | 1 3 3 1 |
| 4 | 1 4 6 4 1 |
| 5 | 1 5 10 10 5 1 |

每个数等于它左上和正上两个数之和。这一递推只用加法，取模随便做；代价是 $O(n^2)$ 的表，$n$ 到几千还行，到 $10^5$ 就不行了。

### 3. 阶乘 + 逆阶乘：$O(1)$ 查一个组合数

$n$ 到 $10^5 \sim 10^6$ 时，直接用公式。公式里有除法，取模下要换成乘逆元（[快速幂与取模](./modular) 第 3 节）：

$$
C(n, k) \bmod p = n! \cdot (k!)^{-1} \cdot \big((n-k)!\big)^{-1} \bmod p
$$

预处理两张表：

- `fact[i]` $= i! \bmod p$，从前往后乘：`fact[i] = fact[i-1] * i`
- `inv_fact[i]` $= (i!)^{-1} \bmod p$。只对最后一个求一次逆元（快速幂），然后**从后往前**：

$$
(i-1)!^{-1} = i!^{-1} \cdot i
$$

因为 $(i-1)! = i! / i$，取倒数就是 $i!^{-1}$ 乘上 $i$。整张表 $O(N)$ 预处理、只用一次快速幂，之后每个 $C(n, k)$ 是 $O(1)$。

### 4. 隔板法：分相同的东西

**问题**：$n$ 颗一样的糖分给 $k$ 个人，每人可以拿 0 颗，有几种分法？也就是求

$$
x_1 + x_2 + \cdots + x_k = n, \qquad x_i \ge 0
$$

的整数解个数。

**直觉**：把 $n$ 颗糖排成一排，往里插 $k-1$ 块隔板，隔板把糖切成 $k$ 段，第 $i$ 段给第 $i$ 个人。
两块隔板挨着，就是中间那个人拿 0 颗。

一共 $n + (k-1)$ 个位置，挑出其中 $k-1$ 个放隔板，其余放糖：

$$
\text{分法数} = C(n + k - 1,\ k - 1)
$$

例：3 颗糖分给 2 个人，$C(4, 1) = 4$。逐个对应：

| 排列 | 分法 |
|---|---|
| `|●●●` | (0, 3) |
| `●|●●` | (1, 2) |
| `●●|●` | (2, 1) |
| `●●●|` | (3, 0) |

**每人至少 1 颗**：先每人发 1 颗，剩下 $n - k$ 颗按上面随便分，$C(n - 1, k - 1)$。

### 5. 容斥：给每个人加上限

**问题**：还是 $x_1 + \cdots + x_k = n$，但每人最多 `limit` 颗。

上限不好直接数，**反过来数「有人超限」的，再减掉**。记 $A_i$ = 第 $i$ 个人超限（$x_i \ge \text{limit}+1$）的分法集合：

$$
\text{答案} = \text{全部} - |A_1 \cup A_2 \cup \cdots \cup A_k|
$$

并集用容斥展开，加一层减一层：

$$
|A_1 \cup \cdots \cup A_k| = \sum_i |A_i| - \sum_{i<j} |A_i \cap A_j| + \sum_{i<j<l} |A_i \cap A_j \cap A_l| - \cdots
$$

**每一项怎么算**：「指定的 $j$ 个人都超限」，就先给这 $j$ 个人各发 $\text{limit}+1$ 颗，剩下的随便分，回到隔板法：

$$
|A_{i_1} \cap \cdots \cap A_{i_j}| = C\big(n - j(\text{limit}+1) + k - 1,\ k - 1\big)
$$

剩下的是负数就是 0 种。这个数只和 $j$ 有关，和选的是哪几个人无关，所以同一层的 $C(k, j)$ 项可以合并：

$$
\text{答案} = \sum_{j=0}^{k} (-1)^j\, C(k, j)\, C\big(n - j(\text{limit}+1) + k - 1,\ k - 1\big)
$$

**为什么容斥是对的**：一个恰好有 $t \ge 1$ 个人超限的分法，在第 $j$ 层被数了 $C(t, j)$ 次，带符号加起来是

$$
\sum_{j=0}^{t} (-1)^j C(t, j) = (1 - 1)^t = 0
$$

正好被消掉；没人超限的分法（$t = 0$）只在 $j = 0$ 被数一次，留下来。$\blacksquare$

### 6. Catalan 数：不交叉的配对

**问题（1259）**：圆上 $2m$ 个人两两握手，手臂不能交叉，有几种方式？

**递推**：盯住 1 号，他和某个人握手，这条线把圆切成两边。线两边的人只能在各自那边握手（跨过去就交叉了），
所以两边各自是一个更小的同类问题。设 1 号的那条线左边有 $\text{left}$ 对、右边有 $m - 1 - \text{left}$ 对：

$$
\text{Cat}(0) = 1, \qquad \text{Cat}(m) = \sum_{\text{left}=0}^{m-1} \text{Cat}(\text{left}) \cdot \text{Cat}(m - 1 - \text{left})
$$

前几项：$1, 1, 2, 5, 14, 42, 132, 429$。闭式是 $\text{Cat}(m) = \dfrac{1}{m+1} C(2m, m)$。

**同一个数列的其他样子**：$m$ 对括号的合法序列数、$m$ 个点的二叉树形状数（[96. Unique Binary Search Trees](https://leetcode.com/problems/unique-binary-search-trees/)）、出栈序列数。
共同点都是「第一个东西把剩下的切成独立的两半」。

### 7. 第一类斯特林数：从左边看得见几根（1866）

**问题**：长度 $1 \dots n$ 的 $n$ 根木棍排成一排，从左边看，恰好看见 $k$ 根（一根被它左边更高的挡住就看不见），有几种排法？

**递推**：盯住**最短的那根**。先把其余 $n-1$ 根排好，再把最短的插进去，一共 $n$ 个空位：

- 插在最左边：它前面没人，看得见；而它最矮，挡不住后面任何一根。其余 $n-1$ 根要贡献 $k-1$ 根看得见：$c(n-1, k-1)$
- 插在其余 $n-1$ 个空位：它前面总有更高的，看不见；也挡不住别人。其余 $n-1$ 根要贡献 $k$ 根：$(n-1) \cdot c(n-1, k)$

$$
c(n, k) = c(n-1, k-1) + (n-1)\, c(n-1, k), \qquad c(0, 0) = 1
$$

| n | c(n, 1..n) |
|---|---|
| 1 | 1 |
| 2 | 1 1 |
| 3 | 2 3 1 |
| 4 | 6 11 6 1 |
| 5 | 24 50 35 10 1 |

这就是（无符号）第一类斯特林数，原本的意思是「$n$ 个元素的排列里恰好有 $k$ 个环」的个数，和 1866 是同一个递推。

**为什么盯最短的**：盯最高的也能做，但最高的会挡住它后面所有人，插进去会改变别人看不看得见。挑一个「插进去不影响别人」的元素，转移才干净。

## 模板

::: code-group

```python [组合数 · 阶乘 + 逆阶乘]
MOD = 10**9 + 7
N = 2 * 10**5 + 1                       # 比题目里最大的 n 大一点

fact = [1] * N
for i in range(1, N):
    fact[i] = fact[i - 1] * i % MOD

inv_fact = [1] * N
inv_fact[N - 1] = pow(fact[N - 1], MOD - 2, MOD)   # 只求一次逆元: 费马小定理
for i in range(N - 1, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % MOD          # (i-1)!^-1 = i!^-1 * i

def C(n, r):
    if r < 0 or r > n:
        return 0
    return fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD
```

```python [组合数 · 杨辉三角]
def pascal(n_max, mod=10**9 + 7):
    """table[n][r] = C(n, r) % mod。只用加法, 模数不是质数也能用。O(n_max^2)。"""
    table = [[0] * (n_max + 1) for _ in range(n_max + 1)]
    for n in range(n_max + 1):
        table[n][0] = 1
        for r in range(1, n + 1):
            table[n][r] = (table[n - 1][r - 1] + table[n - 1][r]) % mod
    return table
```

```python [隔板 + 容斥]
from math import comb

def stars_bars(total, people):
    """total 个相同的球分给 people 个人, 每人 >= 0。total < 0 时没有分法。"""
    if total < 0:
        return 0
    return comb(total + people - 1, people - 1)

def bounded(total, people, limit):
    """每人 0..limit 的分法数。容斥: 枚举「至少 j 个人超限」。"""
    over = limit + 1
    ans = 0
    for j in range(people + 1):
        sign = 1 if j % 2 == 0 else -1
        rest = total - j * over            # 选中的 j 个人先各拿走 limit+1 颗
        ans += sign * comb(people, j) * stars_bars(rest, people)
    return ans
```

```python [验证]
import random
from itertools import product
from math import comb

for _ in range(2000):
    n = random.randrange(N)
    r = random.randrange(-2, n + 3)
    assert C(n, r) == (comb(n, r) % MOD if 0 <= r <= n else 0)

table = pascal(60)
assert all(table[n][r] == comb(n, r) % MOD for n in range(61) for r in range(n + 1))

for total in range(13):
    for people in range(1, 5):
        for limit in range(6):
            brute = sum(1 for xs in product(range(limit + 1), repeat=people) if sum(xs) == total)
            assert bounded(total, people, limit) == brute
```

:::

**Python 里能不能直接 `math.comb`**：能，它算出精确的大整数，再 `% MOD`。$n$ 在几千以内、只算几次，直接用；
$n$ 到 $10^5$ 以上或者要算很多次，大整数越来越慢，换成阶乘表。

## 例子

### 2400. 恰好 k 步走到终点：推出一个组合数

数轴上从 `startPos` 出发，每步左或右走 1，恰好 `k` 步到 `endPos`，有几种走法？

**建模**：设 $d = \text{endPos} - \text{startPos}$（要净往右挪几格），往右 $r$ 步、往左 $l$ 步：

$$
r + l = k \ \ (\text{一共 } k \text{ 步}), \qquad r - l = d \ \ (\text{净挪 } d \text{ 格})
$$

两式相加 $2r = k + d$，所以 $r = \dfrac{k + d}{2}$。左右各走几步定死了，不同的只是「哪几步往右」：

$$
\text{答案} = C(k, r)
$$

**两个前提**：$r$ 和 $l$ 得是能真走出来的步数，也就是非负整数。

- **$k + d$ 必须是偶数**。任何一条真实的路都有 $k + d = (r + l) + (r - l) = 2r$，是偶数；$k + d$ 是奇数就一条路都没有。
  直觉：每走一步位置的奇偶翻一次，走 $k$ 步后的奇偶是定死的。
- **$|d| \le k$**。一步只挪一格，$k$ 步最多挪 $k$ 格；否则 $r$ 或 $l$ 是负数。

```python
from math import comb

class Solution:
    def numberOfWays(self, startPos: int, endPos: int, k: int) -> int:
        MOD = 10**9 + 7
        d = endPos - startPos
        if (k + d) % 2 == 1 or abs(d) > k:      # r 不是整数, 或者步数不够
            return 0
        r = (k + d) // 2                        # 往右走几步
        return comb(k, r) % MOD
```

**手推例 1**（`startPos = 1, endPos = 2, k = 3`）：$d = 1$，$r = 2$，$l = 1$，$C(3, 2) = 3$。
三条路正好是「那一步左放在第几步」：

| 走法 | 路径 |
|---|---|
| 右右左 | 1 → 2 → 3 → 2 |
| 右左右 | 1 → 2 → 1 → 2 |
| 左右右 | 1 → 0 → 1 → 2 |

**例 2**（`startPos = 2, endPos = 5, k = 10`）：$d = 3$，$k + d = 13$ 是奇数，答案 0。

### 2929. 三个人分糖，每人有上限：隔板 + 容斥

$n$ 颗糖分给 3 个小孩，每人最多 `limit` 颗，有几种分法？$n, \text{limit} \le 10^6$。

正好是原理第 4、5 节，$k = 3$：

```python
from math import comb

class Solution:
    def distributeCandies(self, n: int, limit: int) -> int:
        def ways(total):                    # 3 个人分 total 颗, 不设上限
            if total < 0:
                return 0
            return comb(total + 2, 2)

        over = limit + 1                    # 超限的人先拿走 limit+1 颗
        ans = 0
        for j in range(4):                  # j = 指定 j 个人超限
            sign = 1 if j % 2 == 0 else -1
            ans += sign * comb(3, j) * ways(n - j * over)
        return ans
```

**手推** `n = 5, limit = 2`（`over = 3`）：

| j | 符号 | C(3, j) | 剩下 | ways(剩下) | 贡献 |
|---|---|---|---|---|---|
| 0 | + | 1 | 5 | C(7, 2) = 21 | +21 |
| 1 | − | 3 | 2 | C(4, 2) = 6 | −18 |
| 2 | + | 3 | −1 | 0 | 0 |
| 3 | − | 1 | −4 | 0 | 0 |

答案 $21 - 18 = 3$，就是 (1, 2, 2)、(2, 1, 2)、(2, 2, 1)。$O(1)$，不用枚举。

### 1866. 看得见 k 根木棍：斯特林递推

原理第 7 节的递推直接写成 DP，`dp[sticks][seen]` = 用 `sticks` 根、看得见 `seen` 根的排法数：

```python
class Solution:
    def rearrangeSticks(self, n: int, k: int) -> int:
        MOD = 10**9 + 7
        dp = [[0] * (k + 1) for _ in range(n + 1)]
        dp[0][0] = 1
        for sticks in range(1, n + 1):
            for seen in range(1, min(sticks, k) + 1):
                shortest_first = dp[sticks - 1][seen - 1]                # 最短的放最左: 看得见
                shortest_hidden = (sticks - 1) * dp[sticks - 1][seen]   # 放在别人后面: 被挡住
                dp[sticks][seen] = (shortest_first + shortest_hidden) % MOD
        return dp[n][k]
```

**手推** `n = 3, k = 2`：答案 $c(3, 2) = 3$。把 3 根的 6 种排法全列出来：

| 排法 | 看得见 |
|---|---|
| 1 2 3 | 3 |
| 1 3 2 | **2** |
| 2 1 3 | **2** |
| 2 3 1 | **2** |
| 3 1 2 | 1 |
| 3 2 1 | 1 |

按递推拆：最短的 1 放最左，剩下 2、3 要看见 1 根，只有 `3 2`，得 `1 3 2`；1 不放最左，剩下要看见 2 根，只有 `2 3`，1 插进它后面两个空位，得 `2 1 3`、`2 3 1`。$1 + 2 \cdot 1 = 3$。✓

$O(nk)$，$n \le 1000$ 时 $10^6$ 次。

### 1259. 握手不交叉：Catalan

原理第 6 节的递推，`cat[m]` 是 $m$ 对人的方式数：

```python
class Solution:
    def numberOfWays(self, numPeople: int) -> int:
        MOD = 10**9 + 7
        pairs = numPeople // 2
        cat = [0] * (pairs + 1)
        cat[0] = 1
        for m in range(1, pairs + 1):
            total = 0
            for left in range(m):            # 1 号和谁握手, 把剩下的人切成两边
                right = m - 1 - left
                total += cat[left] * cat[right]
            cat[m] = total % MOD
        return cat[pairs]
```

`numPeople = 4` 得 2，`numPeople = 6` 得 5。$O(m^2)$；要更快就用闭式 $\text{Cat}(m) = C(2m, m) \cdot (m+1)^{-1}$，配阶乘表 $O(1)$。

## 栽过的坑

- **2400：没判奇偶，WA**。`startPos = 2, endPos = 5, k = 10`，输出 210，应为 0。
  $d = 3$，$k + d = 13$ 是奇数，$r = 6.5$ 根本走不出来；`(k + d) // 2` 把 6.5 截成 6，算出 $C(10, 6) = 210$。
  **`//` 会把「走不到」悄悄截成一个看起来正常的整数**，所以先判 `(k + d) % 2`，再判 `abs(d) > k`（$d < -k$ 时 $r$ 为负，`comb` 直接报错；$d > k$ 时 $r > k$，`comb` 返回 0，碰巧没事）。

## 面试追问

::: details Q：2400 不推公式，能直接 DP 吗？
能。`ways[pos]` = 走了若干步后停在 `pos` 的走法数，每步 `nxt[pos ± 1] += ways[pos]`，走 $k$ 轮。$k \le 1000$，$O(k^2)$ 能过。

位置可能走到负数（起点往左 $k$ 步），数组下标要整体加偏移 $k$，开 $2k + 1$ 格：

```python
def numberOfWays(startPos, endPos, k):
    MOD = 10**9 + 7
    offset = k                              # 下标 offset 代表 startPos
    width = 2 * k + 1
    ways = [0] * width
    ways[offset] = 1
    for _ in range(k):
        nxt = [0] * width
        for idx in range(width):
            if ways[idx] == 0:
                continue
            if idx - 1 >= 0:
                nxt[idx - 1] = (nxt[idx - 1] + ways[idx]) % MOD
            if idx + 1 < width:
                nxt[idx + 1] = (nxt[idx + 1] + ways[idx]) % MOD
        ways = nxt
    target = endPos - startPos + offset
    return ways[target] if 0 <= target < width else 0
```

这个 DP 每一轮就是杨辉三角的一行，所以最后得到的正是 $C(k, r)$。
:::

::: details Q：为什么 inv_fact 要从后往前推，不对每个 i 单独求逆元？
单独求每个要一次快速幂，$O(N \log p)$。从后往前只求一次，之后每步一次乘法，$O(N + \log p)$。
也可以从前往后：先求所有 $i^{-1}$（有 $O(N)$ 的线性递推），再前缀乘，但不如这个直接。
:::

::: details Q：容斥什么时候能把同一层合并成 $C(k, j)$ 一项？
当「指定的 $j$ 个集合的交」的大小只和 $j$ 有关、和具体选哪几个无关的时候，比如 2929 里三个人的上限一样。
如果每人上限不同，就得老老实实枚举 $2^k$ 个子集。
:::

::: details Q：$n \ge p$ 时阶乘表还能用吗？
不能：$n!$ 里含因子 $p$，模下是 0，逆元不存在。这时要用 Lucas 定理把 $n, k$ 拆成 $p$ 进制逐位算。
LC 里模数都是 $10^9 + 7$、$n$ 远小于它，碰不到。
:::
