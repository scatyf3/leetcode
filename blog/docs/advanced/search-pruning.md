---
title: 搜索 + 剪枝
status: draft
order: 9
alias: []
related: [/paradigms/backtracking]
---

# 搜索 + 剪枝

> 剪枝分哪几种、各砍掉多少；1240 为什么贪心和切一刀 DP 都不对，只能搜

## 一句话

没有好的多项式算法、数据又小，就直接暴搜，靠剪枝把搜索树砍小。

## 怎么认出这类题

数据范围小得反常（如 n, m ≤ 13），而且想不出 DP 的状态。

- 试过的贪心 / DP 能找到反例（1240 的 11 × 13）
- 求的是「最少 / 最多」：有一个当前最优解可以拿来剪别的分支

建在 L3 的：[回溯](../paradigms/backtracking)

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| **[1240. Tiling a Rectangle with the Fewest Squares](https://leetcode.com/problems/tiling-a-rectangle-with-the-fewest-squares/)** | 搜索 + 剪枝 |

## 原理

### 1. 剪枝是什么：在搜索树上提前掉头

回溯就是把所有选择画成一棵树、深度优先走一遍（见 [回溯](../paradigms/backtracking)）。
剪枝是走到某个节点时，**能证明它下面不会有更好的答案**，就不往下走。剪得越早，砍掉的子树越大。

下面五种剪枝，数字都是 1240 在 $11 \times 13$ 上实测的「访问了多少个节点」：

| 加了什么 | 节点数 | 说明 |
|---|---|---|
| 什么都不剪 | > 3,000,000（没跑完） | 跑到 300 万个节点时手动停了，当时最好才找到 8 |
| 最优性剪枝，小方块先试 | 586,392 | 能跑完，答案 6 |
| 最优性剪枝，**大方块先试** | 4,793 | 同样的剪枝，换个顺序少两个数量级 |
| 上面那样，但天际线按长边存 | 10,128 | 把矩形转 90° 再搜，多一倍 |
| 不剪枝，改成记忆化 | 75,190 个状态 | 换个思路：同一条天际线只算一次 |

### 2. 五种剪枝

**① 可行性剪枝：这一步根本放不下。** 1240 里方块不能跨出当前那段平地、不能顶出上沿，枚举大小时直接从可行的最大值开始。
这种剪枝通常写在「枚举范围」里，看不出是剪枝，但没有它就会搜一堆非法状态。

**② 最优性剪枝（分支定界）：再走下去也不会比已知最好的更好。** 求最小值时维护全局的 `best`：

$$
\text{当前代价} + \text{剩下至少还要的代价} \ge \text{best} \quad\Longrightarrow\quad \text{剪掉}
$$

「剩下至少还要多少」叫**下界**，估得越紧剪得越多。1240 用的是最粗的下界：已经放了 `count` 块，没铺满就至少还要 1 块，
所以 `count >= best` 时最好也只能打平，直接剪。
下面「最少硬币」那个骨架用了一个更紧的下界：剩下的钱全用当前最大面额，也至少要 $\lceil \text{remain} / \text{coin} \rceil$ 枚。

**③ 搜索顺序：先走最可能好的分支。** 最优性剪枝靠 `best` 剪，`best` 越早变小，后面剪得越狠。
1240 先试大方块，很快就拿到一个 6 块的解，后面凡是用到第 6 块还没铺满的分支全被剪掉：586,392 → 4,793。

**④ 对称性：等价的状态只搜一个。** 两种用法：

- 同一组方块，按不同顺序放进去，是同一种铺法。1240 规定**每次只填最低、最靠左的那个空格**，每种铺法就只会被生成一次（证明见下面例子）。
- 矩形转 90° 答案不变，可以自己挑一个好搜的方向。实测天际线按短边存（11 列、每列高 13）比按长边存（13 列、每列高 11）少一半节点：每一层可选的位置更少。

**⑤ 记忆化：同一个状态只算一次。** 如果「剩下的子问题」只由一个小状态决定，就可以缓存。
1240 剩下要铺的形状完全由天际线 `heights` 决定，可以 `@lru_cache`。11 × 13 共出现 75,190 种天际线。
注意记忆化和最优性剪枝不好一起用：剪枝依赖全局的 `best`，同一个状态在不同时刻被剪的结果不一样，缓存会出错。

### 3. 1240 为什么只能搜

两个看起来对的思路都有反例：

- **贪心**：每次切出能放下的最大正方形（像辗转相除）。$11 \times 13$ 切出来是 8 块。
- **切一刀 DP**：$f(a, b) = \min\big(\min_i f(i, b) + f(a-i, b),\ \min_j f(a, j) + f(a, b-j)\big)$，只允许一刀把矩形切成两个矩形。
  $1 \le n, m \le 13$ 的所有情况里，只有 $11 \times 13$ 算错（给 8）。

正确答案 6 是这样铺的（字母是 6 个正方形，边长 7、4、4、6、1、5）：

```
D D D D D D F F F F F
D D D D D D F F F F F
D D D D D D F F F F F
D D D D D D F F F F F
D D D D D D F F F F F
D D D D D D E C C C C
A A A A A A A C C C C
A A A A A A A C C C C
A A A A A A A C C C C
A A A A A A A B B B B
A A A A A A A B B B B
A A A A A A A B B B B
A A A A A A A B B B B
```

中间那块 1 × 1 的 E 让任何一刀都会切穿某个正方形。切一刀 DP 只能生成「能一刀刀切开」的铺法，所以永远找不到它。

## 模板

::: code-group

```python [分支定界骨架（最少硬币）]
def fewest_coins(coins, amount):
    """演示骨架用。322 正经做法是 DP, 这里只看剪枝怎么写。"""
    coins = sorted(coins, reverse=True)          # ③ 顺序: 大面额先试, 先拿到一个好的 best
    best = float('inf')

    def dfs(i, remain, count):
        nonlocal best
        if remain == 0:
            best = min(best, count)
            return
        if i == len(coins):                      # ① 可行性: 没币可用了
            return
        coin = coins[i]
        lower = count + (remain + coin - 1) // coin   # 剩下全用当前最大面额也至少要这么多
        if lower >= best:                        # ② 最优性: 下界都不比 best 好
            return
        max_take = remain // coin
        for take in range(max_take, -1, -1):     # 这种面额拿几枚, 多的先试
            dfs(i + 1, remain - take * coin, count + take)

    dfs(0, amount, 0)
    return best if best != float('inf') else -1
```

```python [天际线 DFS（1240）]
class Solution:
    def tilingRectangle(self, n: int, m: int) -> int:
        height, width = max(n, m), min(n, m)     # ④ 天际线按短边存: 列少, 每层选择少
        heights = [0] * width                    # heights[c]: 第 c 列已经铺到多高
        best = n * m                             # 初始上界: 全用 1x1

        def dfs(count):
            nonlocal best
            if count >= best:                    # ② 最优性剪枝
                return
            low = min(heights)
            if low == height:                    # 铺满了
                best = count
                return
            start = heights.index(low)           # ④ 只填最低、最靠左的那一格
            end = start
            while end < width and heights[end] == low:
                end += 1                         # [start, end) 是一段同样高的平地
            max_size = min(end - start, height - low)   # ① 可行性: 不跨出平地, 不顶出上沿
            for size in range(max_size, 0, -1):         # ③ 顺序: 大的先试
                for c in range(start, start + size):
                    heights[c] += size
                dfs(count + 1)
                for c in range(start, start + size):    # 回溯: 拿掉这块
                    heights[c] -= size

        dfs(0)
        return best
```

```python [验证]
import random
from functools import lru_cache

def coins_dp(coins, amount):
    INF = float('inf')
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

for _ in range(2000):
    coins = random.sample(range(1, 30), random.randrange(1, 5))
    amount = random.randrange(0, 200)
    assert fewest_coins(coins, amount) == coins_dp(coins, amount)

def tiling_memo(n, m):                 # 不剪枝, 天际线记忆化, 独立算一遍
    height, width = max(n, m), min(n, m)

    @lru_cache(maxsize=None)
    def go(h):
        low = min(h)
        if low == height:
            return 0
        start = h.index(low)
        end = start
        while end < width and h[end] == low:
            end += 1
        return min(1 + go(tuple(x + s if start <= i < start + s else x for i, x in enumerate(h)))
                   for s in range(1, min(end - start, height - low) + 1))
    return go((0,) * width)

S = Solution()
assert S.tilingRectangle(2, 3) == 3 and S.tilingRectangle(5, 8) == 5 and S.tilingRectangle(11, 13) == 6
for n in range(1, 11):
    for m in range(1, 11):
        assert S.tilingRectangle(n, m) == tiling_memo(n, m)
```

:::

## 例子

### 1240. Tiling a Rectangle with the Fewest Squares

$n, m \le 13$，用最少的正方形铺满 $n \times m$ 矩形。代码就是上面的模板。

**状态怎么表示：天际线。** 每次都填最低、最靠左的空格，所以已铺部分永远是「从底往上长」的一排柱子，
只用一个数组 `heights[c]` 记每列铺到多高。

**为什么每种铺法只会搜到一次。** 设最低、最靠左的空格是 $(\text{low}, \text{start})$：

- 它下面的格子都铺了（它是最低的）
- 它左边那一格也铺了（`start` 左边的列都比 `low` 高）

所以盖住它的那个正方形，**左下角一定就在这一格**。DFS 在这一格枚举正方形的边长，把所有可能都试到，也不会重复。
边长的上限：不能盖到右边更高的柱子（≤ 平地宽度 `end - start`），不能顶出上沿（≤ `height - low`）。

**手推 $2 \times 3$**（`height = 3`，`width = 2`，`heights` 从左到右）：

| 步 | 动作 | heights | 放了几块 | 说明 |
|---|---|---|---|---|
| 1 | 在 (0, 0) 放 2 × 2 | [2, 2] | 1 | 平地宽 2、上面还剩 3，最大放 2 |
| 2 | 在 (2, 0) 放 1 × 1 | [3, 2] | 2 | 只剩 1 行高 |
| 3 | 在 (2, 1) 放 1 × 1 | [3, 3] | 3 | 铺满，`best = 3` |
| 4 | 回到第 1 步，改放 1 × 1 | [1, 0] | 1 | |
| 5 | 在 (0, 1) 放 1 × 1 | [1, 1] | 2 | |
| 6 | 在 (1, 0) 放 2 × 2 | [3, 3] | 3 | 3 ≥ best，剪掉 |
| 7 | 改放 1 × 1 | [2, 1] | 3 | 3 ≥ best，剪掉 |

答案 3。第 6、7 步就是最优性剪枝：已经用了 3 块，再好也只能打平，不往下走。

**复杂度**：没有好的上界，靠剪枝。$1 \le n, m \le 13$ 全部 169 种输入一共不到 0.1 秒（本地 Python）。

## 栽过的坑

只收自己真栽过的。

## 面试追问

::: details Q：剪枝之后复杂度是多少？
说不准。剪枝改变的是实际访问的节点数，最坏情况的上界通常还是指数级。所以这类题要靠「数据范围小」兜底，答的时候说清楚：
最坏指数，实际靠剪枝，给出实测的规模。
:::

::: details Q：最优性剪枝和记忆化为什么不能简单叠加？
记忆化缓存的是「这个状态往下的最优值」，前提是这个值和怎么走到这里无关。
最优性剪枝让 dfs 的返回结果依赖全局的 `best`：同一个状态，早访问时没被剪、晚访问时被剪了，缓存里存的就不是真正的最优值。
要叠加，得把「被剪掉」和「算出了真值」分开存，或者把 bound 也当成状态的一部分。
:::

::: details Q：下界怎么估得更紧？
估的是「剩下的部分至少还要多少代价」，必须是真的下界（不能估多），否则会剪掉最优解。
常见来源：松弛约束后的最优值（如硬币题允许拿小数枚 → $\lceil \text{remain} / \text{最大面额} \rceil$）、剩余量除以单步最大贡献。
:::
