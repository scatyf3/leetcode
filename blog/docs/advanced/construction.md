---
title: 构造
status: draft
order: 10
alias: []
related: []
---

# 构造

> 没有搜索空间可走时怎么找答案：小数据暴搜 → 看出规律 → 证明它对；667 的锯齿、932 的奇偶分治

## 一句话

不搜索、也不 DP，直接给出一个满足条件的答案。难在观察，代码往往很短。

## 怎么认出这类题

题目要求「返回任意一个满足条件的数组」。

建在 L3 的：—— 不太依赖 L3 的哪个套路，靠观察

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| [667. Beautiful Arrangement II](https://leetcode.com/problems/beautiful-arrangement-ii/) | 构造入门 |
| **[932. Beautiful Array](https://leetcode.com/problems/beautiful-array/)** | 构造 |

## 原理

### 1. 构造题的三步

构造题的 $n$ 通常到 $10^3 \sim 10^4$，排列有 $n!$ 个，搜不动；可题目只要**任意一个**答案，所以要的是一条规则，按规则直接把答案写出来。规则从哪来：

1. **小数据暴搜**：$n \le 8$ 时把所有排列枚举一遍，把满足条件的全打印出来。
2. **找规律**：在一堆答案里挑一个「长得最整齐」的，看它是怎么排的（升序？左右交替？奇偶分开？）。
3. **证明**：说清楚这条规则为什么对**所有** $n$ 都成立。证不出来，就再用暴搜对拍到 $n = 100$ 左右。

第 1 步和第 3 步的代码见下面模板：一个暴搜器，一个检查器。

### 2. 667：用锯齿造出 k 种差

**题意**：用 $1 \dots n$ 排一个排列，让相邻两数之差的绝对值**恰好有 $k$ 种**（$1 \le k < n$）。

**小数据**：$n = 4, k = 3$ 暴搜出来是

```
(1, 4, 2, 3)  (2, 3, 1, 4)  (3, 2, 4, 1)  (4, 1, 3, 2)
```

看 `1, 4, 2, 3`：差是 $3, 2, 1$。**从两头往中间交替取**，差一次比一次少 1。

**规律**：在 $k+1$ 个连续整数 $[\text{low}, \text{high}]$ 里，按「最小、最大、次小、次大……」排，差依次是

$$
k,\ k-1,\ k-2,\ \dots,\ 1
$$

每取一个，剩下的区间就缩 1，下一步跨过的距离也就少 1。这一段正好造出 $k$ 种差。

剩下的 $n - k - 1$ 个数怎么办？让它们**升序**排在前面，相邻差都是 1，而 1 已经在锯齿那段里出现过了，不会多出新的差。

$$
\underbrace{1,\ 2,\ \dots,\ n-k-1}_{\text{差全是 } 1},\ \underbrace{n-k,\ n,\ n-k+1,\ n-1,\ \dots}_{\text{差是 } k, k-1, \dots, 1}
$$

接缝处 $n-k-1 \to n-k$ 的差也是 1。所以总共恰好 $k$ 种。$\blacksquare$

**手推** $n = 8, k = 3$：

| 排列 | 1 | 2 | 3 | 4 | 5 | 8 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| 和前一个的差 | | 1 | 1 | 1 | 1 | **3** | **2** | 1 |

差的种类 $\{1, 2, 3\}$，正好 3 种。

### 3. 932：奇偶分治

**题意**：用 $1 \dots n$ 排一个排列，不存在 $i < m < j$ 使得 $2 \cdot A[m] = A[i] + A[j]$，也就是**任意两个数的平均数都不夹在它们中间**。

**观察 1：奇数放左边、偶数放右边，跨两边的三元组一定安全。**
若 $A[i]$ 是奇数、$A[j]$ 是偶数，$A[i] + A[j]$ 是奇数，不可能等于 $2 \cdot A[m]$。
所以坏三元组只可能两头都在奇数那半边，或都在偶数那半边，问题缩小成「两半各自美丽」。

但光分一次奇偶不够：奇数那半边 `1, 3, 5` 里 $2 \cdot 3 = 1 + 5$，还是坏的。要在每半边里**接着分**。

**观察 2：美丽数组做线性变换还是美丽的。**
若 $A$ 美丽，把每个数换成 $p \cdot x + q$（$p \ne 0$）：

$$
2(p a_m + q) = (p a_i + q) + (p a_j + q) \iff 2 a_m = a_i + a_j
$$

等式两边同时乘 $p$、同时加 $2q$，成立与否不变。所以坏三元组变换前后一一对应，**美丽性不变**。

**合起来**：$1 \dots n$ 里的奇数是 $2x - 1$（$x = 1 \dots \lceil n/2 \rceil$），偶数是 $2x$（$x = 1 \dots \lfloor n/2 \rfloor$）。

- 先递归造出长度 $\lceil n/2 \rceil$ 的美丽数组，每个数做 $x \mapsto 2x - 1$，得到所有奇数的美丽排列
- 再递归造出长度 $\lfloor n/2 \rfloor$ 的，每个数做 $x \mapsto 2x$，得到所有偶数的美丽排列
- 奇数段接偶数段：段内由观察 2 保证，跨段由观察 1 保证。$\blacksquare$

**手推** $n = 5$：

| 调用 | 奇数部分 | 偶数部分 | 结果 |
|---|---|---|---|
| beautiful(1) | | | [1] |
| beautiful(2) | [1] → [1] | [1] → [2] | [1, 2] |
| beautiful(3) | beautiful(2) = [1, 2] → [1, 3] | [1] → [2] | [1, 3, 2] |
| beautiful(5) | beautiful(3) = [1, 3, 2] → [1, 5, 3] | beautiful(2) = [1, 2] → [2, 4] | **[1, 5, 3, 2, 4]** |

`n = 8` 时结果是 `[1, 5, 3, 7, 2, 6, 4, 8]`。

## 模板

::: code-group

```python [暴搜找规律]
from itertools import permutations

def show_small(n, ok, limit=10):
    """把 1..n 的所有排列里满足 ok 的打印出来, 用来找规律。n <= 8 左右。"""
    found = [p for p in permutations(range(1, n + 1)) if ok(p)]
    print(f"n={n}: {len(found)} 个")
    for p in found[:limit]:
        print("  ", p)

# 667: 相邻差恰好 k 种
def distinct_diffs(arr):
    return len({abs(arr[i + 1] - arr[i]) for i in range(len(arr) - 1)})

show_small(4, lambda p: distinct_diffs(p) == 3)
```

```python [检查器 + 对拍]
def is_beautiful(arr):
    """932 的检查器: 不存在 i < m < j 使 2*arr[m] == arr[i] + arr[j]。O(n^2)。"""
    pos = {value: idx for idx, value in enumerate(arr)}
    n = len(arr)
    for i in range(n):
        for j in range(i + 2, n):
            total = arr[i] + arr[j]
            if total % 2 == 0:
                mid = total // 2
                if i < pos[mid] < j:          # 平均数夹在中间
                    return False
    return True

def check_construction(build, ok, n_max):
    """对 n = 1..n_max 逐个检查: 是 1..n 的排列, 并且满足条件。"""
    for n in range(1, n_max + 1):
        arr = build(n)
        assert sorted(arr) == list(range(1, n + 1)), n
        assert ok(arr), (n, arr)
```

```python [验证]
from itertools import permutations

# 检查器本身先和 O(n^3) 的定义对拍
def is_beautiful_brute(arr):
    n = len(arr)
    return not any(2 * arr[m] == arr[i] + arr[j]
                   for i in range(n) for m in range(i + 1, n) for j in range(m + 1, n))

for n in range(1, 9):
    for p in permutations(range(1, n + 1)):
        assert is_beautiful(p) == is_beautiful_brute(p)

check_construction(beautifulArray, is_beautiful, 120)       # 932, 见下面例子
for n in range(2, 60):                                       # 667, 每个 k 都试
    for k in range(1, n):
        arr = constructArray(n, k)
        assert sorted(arr) == list(range(1, n + 1))
        assert distinct_diffs(arr) == k
```

:::

## 例子

### 667. Beautiful Arrangement II：升序 + 锯齿

```python
class Solution:
    def constructArray(self, n: int, k: int) -> list[int]:
        ans = list(range(1, n - k))             # 前 n-k-1 个: 1, 2, ..., n-k-1, 相邻差都是 1
        low, high = n - k, n                    # 剩下 k+1 个数在 [n-k, n] 里左右交替取
        take_low = True
        while low <= high:
            if take_low:
                ans.append(low)
                low += 1
            else:
                ans.append(high)
                high -= 1
            take_low = not take_low
        return ans
```

- $k = n - 1$ 时升序那段是空的，整个就是锯齿：$n = 5$ 得 `[1, 5, 2, 4, 3]`，差 $4, 3, 2, 1$。
- $O(n)$ 时间，除了答案不占额外空间。

### 932. Beautiful Array：奇偶分治

```python
class Solution:
    def beautifulArray(self, n: int) -> list[int]:
        if n == 1:
            return [1]
        odd_part = self.beautifulArray((n + 1) // 2)    # 1..n 里有 (n+1)//2 个奇数
        even_part = self.beautifulArray(n // 2)         # 和 n//2 个偶数
        odds = [2 * x - 1 for x in odd_part]            # 线性变换, 美丽性不变
        evens = [2 * x for x in even_part]
        return odds + evens                             # 跨两段: 奇 + 偶 是奇数, 安全
```

**复杂度**：每层把所有数各变换一次，共 $O(\log n)$ 层，$O(n \log n)$。
同一个 $n$ 会被重复调用（比如 `beautiful(5)` 和 `beautiful(4)` 都要 `beautiful(2)`），加 `@cache` 能省掉重复，但不影响量级。

## 栽过的坑

只收自己真栽过的。

## 面试追问

::: details Q：932 为什么不能只分一次奇偶？
分一次只保证「跨奇偶两段」的三元组安全。奇数段内部照样可能坏：`[1, 3, 5]` 里 $2 \cdot 3 = 1 + 5$。
所以每一段内部要继续分，靠线性变换把「$\lceil n/2 \rceil$ 个奇数」变回「$1 \dots \lceil n/2 \rceil$」这个同类的小问题。
:::

::: details Q：932 有不用递归的写法吗？
有。把 $x - 1$ 写成固定位宽的二进制，**按位反转后的值排序**，得到的就是同一个数组：

```python
def beautifulArray(n):
    width = max(1, (n - 1).bit_length())
    def reversed_bits(x):
        return int(format(x - 1, f'0{width}b')[::-1], 2)
    return sorted(range(1, n + 1), key=reversed_bits)
```

原因：递归每一层按「当前最低位」把数分成两组（先 0 后 1），一层层往高位走。这正好等价于先比最低位、再比次低位……也就是按反转后的二进制排序。
`n = 8` 时两种写法都是 `[1, 5, 3, 7, 2, 6, 4, 8]`。
:::

::: details Q：构造题想不出规律怎么办？
先确认是不是真的构造题：数据范围小（$n \le 12$）就直接搜；有「最少 / 最多」就多半是贪心或 DP。

确认是构造，就把小数据的**全部答案**打出来，看有没有一个特别整齐的；再试着从 $n$ 的答案推出 $n+1$ 或 $2n$ 的答案（932 就是从 $n/2$ 推 $n$）。
规律只在小数据上成立的情况很常见，所以最后一定要用检查器对拍到大一点的 $n$。
:::
