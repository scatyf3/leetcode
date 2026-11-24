---
title: 状压 DP
status: draft
order: 7
alias: []
related: [/paradigms/bit-manipulation, /paradigms/1d-dp]
---

# 状压 DP

> 子集怎么变成一个整数；按 mask 从小到大填表为什么对；枚举子集的子集为什么是 $3^n$；什么时候还要多带一维「最后一个」

## 一句话

n ≤ 20 时，「哪些元素已经用过」可以压成一个整数 `mask`，当作 DP 的状态。
状态数是 $2^n$，$n = 20$ 时约一百万，正好能跑。

## 怎么认出这类题

某个维度只有十几；状态是「一个子集」。

- 数据范围：$n \le 20$ 左右（$2^n \cdot n$ 能跑），或 $n \le 14$ 左右（$3^n$ 能跑）
- 题面：把 n 个东西分组 / 排顺序 / 两两配对，而且「哪些已经处理过」会影响后面

建在 L3 的：[位运算](../paradigms/bit-manipulation) · [一维 DP](../paradigms/1d-dp)

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| **[1986. Minimum Number of Work Sessions to Finish the Tasks](https://leetcode.com/problems/minimum-number-of-work-sessions-to-finish-the-tasks/)** | 状压 DP |

## 原理

### 1. 子集 = 一个整数

n 个元素编号 $0 \dots n-1$，一个子集 $S$ 写成 n 位二进制数：第 $i$ 位是 1 表示元素 $i$ 在 $S$ 里。

例：$n = 4$，$S = \{0, 1, 3\}$ 写成 $1011_2 = 11$（最右边是第 0 位）。

所有子集正好是 $0 \dots 2^n - 1$ 这些整数，空集是 0，全集是 $2^n - 1$。数组下标直接用 mask：`dp[mask]`。

**常用操作**（Python）：

| 想做的事 | 写法 | 例：mask = `1011` |
|---|---|---|
| 元素 $i$ 在不在 | `(mask >> i) & 1` | $i = 2$ → 0 |
| 加入元素 $i$ | `mask \| (1 << i)` | $i = 2$ → `1111` |
| 去掉元素 $i$（已知在） | `mask ^ (1 << i)` | $i = 0$ → `1010` |
| 全集 | `(1 << n) - 1` | `1111` |
| 补集 | `full ^ mask` | `0100` |
| 最低位的 1 | `mask & -mask` | `0001` |
| 元素个数 | `bin(mask).count('1')` | 3 |
| `sub` 是不是 `mask` 的子集 | `(sub & mask) == sub` | |

`mask & -mask` 为什么是最低位的 1，见 [位运算](../paradigms/bit-manipulation)。

### 2. 在 mask 上做 DP

**状态**：`dp[mask]` = 只考虑 mask 里那些元素时的最优值 / 方案数。

**转移**：从 mask 里拿掉一部分，落到一个更小的 mask：

$$
\text{dp}[\text{mask}] = \min_{\text{拿掉的部分 } T \subseteq \text{mask}} \Big( \text{dp}[\text{mask} \setminus T] + \text{cost}(T) \Big)
$$

**填表顺序**：拿掉若干个 1，整数一定变小（$\text{mask} \setminus T = \text{mask} - T$）。
所以 **mask 从 0 到 $2^n - 1$ 顺着填**，算 `dp[mask]` 时用到的格子都已经填好了，不用想拓扑序。

**最简单的例子：子集和**。`total[mask]` = mask 里元素的和。拿掉最低位那一个元素：

$$
\text{total}[\text{mask}] = \text{total}[\text{mask} \oplus \text{low}] + \text{nums}[\text{idx}(\text{low})], \qquad \text{low} = \text{mask} \mathbin{\&} (-\text{mask})
$$

每个 mask 只做 O(1)，$O(2^n)$ 预处理出所有子集的和。很多题第一步都是它。

### 3. 枚举子集的子集：为什么是 $3^n$

有的题一次要拿掉「一组」：`dp[mask]` 要枚举 mask 的所有非空子集 `sub`。写法：

```python
sub = mask
while sub > 0:
    # 处理 sub
    sub = (sub - 1) & mask
```

**为什么能不重不漏**：`sub - 1` 把 sub 最低位的 1 变成 0、它右边的 0 全变成 1；
再 `& mask`，把不属于 mask 的位清掉。结果就是「在 mask 的位上，比 sub 小的最大的那个子集」。
所以它从 mask 开始，**按从大到小的顺序**走遍 mask 的每个子集。

例：mask = `1011`，依次得到 `1011, 1010, 1001, 1000, 0011, 0010, 0001`，共 $2^3 - 1 = 7$ 个。

**总次数**：外层枚举所有 mask、内层枚举它的子集，总共是多少？
看每个元素：它要么不在 mask 里，要么在 mask 里但不在 sub 里，要么在 sub 里，三种情况。
所以 (mask, sub) 这样的对一共 $3^n$ 个。也可以用二项式定理算：

$$
\sum_{\text{mask}} 2^{|\text{mask}|} = \sum_{k=0}^{n} \binom{n}{k} 2^k = (1 + 2)^n = 3^n
$$

$n = 14$ 时 $3^{14} \approx 4.8 \times 10^6$，能跑；$n = 20$ 时 $3^{20} \approx 3.5 \times 10^9$，跑不动。
**看到 $n \le 14$ 左右，多半就是让你枚举子集。**

### 4. 带「最后一个」：dp[mask][last]

只知道「用过哪些」还不够的题，比如要排一个**顺序**、代价取决于相邻两个（旅行商问题，TSP）：
从 A 走到 B 的代价跟上一站是谁有关，所以状态要多带一维。

**状态**：`dp[mask][last]` = 已经访问过 mask 里的点、现在停在 last，最小代价。

**转移**：下一站 nxt 不在 mask 里：

$$
\text{dp}[\text{mask} \mid \{nxt\}][nxt] = \min\big(\ \cdot\ ,\ \text{dp}[\text{mask}][\text{last}] + \text{dist}[\text{last}][nxt] \big)
$$

**复杂度**：$2^n \cdot n$ 个状态，每个往外推 $n$ 次，$O(2^n n^2)$。$n = 20$ 约 4 亿次，Python 吃力，C++ 能过。
对比暴力枚举排列 $n!$：$20! \approx 2.4 \times 10^{18}$。状压省掉的是「同一个集合、同一个终点，前面怎么排的不重要」。

## 模板

::: code-group

```python [子集和（按最低位拆）]
def subset_sums(nums):
    """total[mask] = mask 里那些元素的和。O(2^n)。"""
    n = len(nums)
    total = [0] * (1 << n)
    for mask in range(1, 1 << n):
        low = mask & -mask                  # 最低位的 1
        idx = low.bit_length() - 1          # 它是第几个元素
        rest = mask ^ low                   # 去掉这个元素, rest < mask, 已经算过
        total[mask] = total[rest] + nums[idx]
    return total
```

```python [枚举子集的子集]
def submasks(mask):
    """mask 的所有非空子集, 从大到小。对所有 mask 一起枚举总共 3^n 次。"""
    out = []
    sub = mask
    while sub > 0:
        out.append(sub)
        sub = (sub - 1) & mask
    return out
```

```python [dp[mask][last]（TSP）]
def tsp(dist):
    """从 0 出发, 每个点恰好走一次, 回到 0 的最短总距离。O(2^n · n^2)。"""
    n = len(dist)
    if n == 1:
        return 0
    INF = float('inf')
    full = (1 << n) - 1
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0                             # 只访问了 0, 停在 0
    for mask in range(1 << n):
        for last in range(n):
            cur = dp[mask][last]
            if cur == INF or not (mask >> last) & 1:
                continue
            for nxt in range(n):
                if (mask >> nxt) & 1:        # 去过了
                    continue
                nxt_mask = mask | (1 << nxt)
                cand = cur + dist[last][nxt]
                if cand < dp[nxt_mask][nxt]:
                    dp[nxt_mask][nxt] = cand
    return min(dp[full][last] + dist[last][0] for last in range(n))
```

```python [验证]
import itertools, random

for _ in range(300):
    n = random.randrange(1, 7)
    nums = [random.randrange(1, 20) for _ in range(n)]
    total = subset_sums(nums)
    for mask in range(1 << n):
        assert total[mask] == sum(nums[i] for i in range(n) if (mask >> i) & 1)

for mask in range(1 << 8):
    expect = [s for s in range(1, 1 << 8) if (s & mask) == s]
    assert sorted(submasks(mask)) == expect
for n in range(1, 13):                       # 连空集一起数, 正好 3^n
    assert sum(len(submasks(m)) + 1 for m in range(1 << n)) == 3 ** n

def tsp_brute(dist):
    n = len(dist)
    if n == 1:
        return 0
    best = float('inf')
    for perm in itertools.permutations(range(1, n)):
        path = (0,) + perm + (0,)
        best = min(best, sum(dist[path[i]][path[i + 1]] for i in range(n)))
    return best

for _ in range(200):
    n = random.randrange(1, 7)
    dist = [[0 if i == j else random.randrange(1, 30) for j in range(n)] for i in range(n)]
    assert tsp(dist) == tsp_brute(dist)
```

:::

## 例子

### 1986. Minimum Number of Work Sessions：两种状态设计

$n \le 14$ 个任务，每段工作时间最多 `sessionTime`（≤ 15），每个任务必须在一段里做完。问最少几段。

两种写法，分别对应原理第 3 节和第 2 节。

#### 写法一：枚举「这一段做哪些」，$O(3^n)$

**状态**：`dp[mask]` = 做完 mask 里的任务最少要几段。

**转移**：最后一段做的是 mask 的某个子集 sub，前提是 sub 的总时长装得进一段：

$$
\text{dp}[\text{mask}] = \min_{\substack{\text{sub} \subseteq \text{mask},\ \text{sub} \neq \varnothing \\ \text{total}[\text{sub}] \le T}} \text{dp}[\text{mask} \oplus \text{sub}] + 1
$$

```python
class Solution:
    def minSessions(self, tasks: list[int], sessionTime: int) -> int:
        n = len(tasks)
        full = (1 << n) - 1

        total = [0] * (1 << n)                 # 子集和
        for mask in range(1, 1 << n):
            low = mask & -mask
            idx = low.bit_length() - 1
            total[mask] = total[mask ^ low] + tasks[idx]

        INF = float('inf')
        dp = [INF] * (1 << n)
        dp[0] = 0
        for mask in range(1, 1 << n):
            sub = mask
            while sub > 0:                     # 最后一段做 sub
                if total[sub] <= sessionTime:
                    rest = mask ^ sub
                    cand = dp[rest] + 1
                    if cand < dp[mask]:
                        dp[mask] = cand
                sub = (sub - 1) & mask
        return dp[full]
```

手推 `tasks = [1, 2, 3]`，`sessionTime = 3`（mask 从右往左是任务 0、1、2）：

| mask | 任务 | total | dp | 怎么来的 |
|---|---|---|---|---|
| `001` | {1} | 1 | 1 | 一段装下 |
| `010` | {2} | 2 | 1 | 一段装下 |
| `011` | {1, 2} | 3 | 1 | 一段装下 |
| `100` | {3} | 3 | 1 | 一段装下 |
| `101` | {1, 3} | 4 | 2 | 装不下，拆成 `100` + `001` |
| `110` | {2, 3} | 5 | 2 | 拆成 `100` + `010` |
| `111` | 全部 | 6 | **2** | `100` 一段，`011` 一段 |

#### 写法二：一个一个加任务，状态记 (段数, 最后一段用了多久)，$O(2^n \cdot n)$

**状态**：`dp[mask]` = 做完 mask 里的任务时，**(用了几段, 最后一段已经用掉的时间)**，两个都越小越好，按字典序比较取最小。

**转移**：最后加进来的是任务 $i$。前一个状态是 (s, u)：

- $u + t_i \le T$：塞进最后一段，变成 $(s,\ u + t_i)$
- 否则新开一段，变成 $(s + 1,\ t_i)$

**为什么能按字典序取最小**：同一个 mask 的两个状态 $(s, u)$ 和 $(s', u')$：

- $s < s'$：前者随时可以新开一段，变成 $(s + 1, 0)$，段数不超过 $s'$，最后一段还是空的。后者往后能做到的，前者都能做到。
- $s = s'$、$u < u'$：段数一样，前者最后一段剩的时间更多，同样不会更差。

所以只保留字典序最小的那个，不会丢掉最优解。（上面的代码也和暴力枚举对拍过。）

```python
class Solution:
    def minSessions(self, tasks: list[int], sessionTime: int) -> int:
        n = len(tasks)
        full = (1 << n) - 1
        INF = (float('inf'), float('inf'))
        dp = [INF] * (1 << n)
        dp[0] = (1, 0)                         # 开了 1 段, 用了 0
        for mask in range(1, 1 << n):
            best = INF
            for i in range(n):
                if not (mask >> i) & 1:
                    continue
                prev_sessions, prev_used = dp[mask ^ (1 << i)]   # 最后加的是任务 i
                if prev_used + tasks[i] <= sessionTime:
                    cand = (prev_sessions, prev_used + tasks[i])
                else:
                    cand = (prev_sessions + 1, tasks[i])
                if cand < best:
                    best = cand
            dp[mask] = best
        return dp[full][0]
```

同一组输入的 dp 表：

| mask | dp | 怎么来的 |
|---|---|---|
| `000` | (1, 0) | 初值 |
| `001` | (1, 1) | 加任务 0（时长 1） |
| `011` | (1, 3) | 在 `001` 上加任务 1，1 + 2 = 3 装得下 |
| `100` | (1, 3) | 加任务 2（时长 3） |
| `101` | (2, 1) | 从 `100` 加任务 0：3 + 1 > 3，新开一段 |
| `110` | (2, 2) | 从 `100` 加任务 1：新开一段 |
| `111` | **(2, 3)** | 从 `110` 加任务 0：2 + 1 = 3 装得下 |

**两种写法比一比**：写法一 $3^{14} \approx 4.8 \times 10^6$，写法二 $2^{14} \cdot 14 \approx 2.3 \times 10^5$，快一个数量级。
写法一的好处是正确性一眼能看出来；写法二要多想一步「为什么字典序最小就够」。

## 栽过的坑

只收自己真栽过的。

## 面试追问

::: details Q：n = 30 还能状压吗？
$2^{30} \approx 10^9$，一个 int 数组就要 4GB，不行。常见出路：折半（meet in the middle），两半各 $2^{15}$ 枚举再合并；
或者换思路，看有没有别的维度小（比如容量、和）能当状态。
:::

::: details Q：dp[mask] 为什么从小到大填就对，不用拓扑排序？
转移只会从 mask 拿掉一些 1，得到的整数一定比 mask 小。整数的大小顺序天然就是一个合法的拓扑序。
:::

::: details Q：TSP 的 dp[mask][last] 能不能去掉 last 这一维？
不能。下一步的代价 dist[last][nxt] 取决于现在停在哪。只记 mask 的话，同一个集合不同终点的两条路混在一起，没法算下一步。
1986 就不需要这一维：加一个任务的代价只跟「最后一段剩多少」有关，那个量已经放进状态里了。
:::
