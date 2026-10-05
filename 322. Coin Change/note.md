# 322. Coin Change

标准1d dp...但感觉写的不是optimal，edgecase很烦人

---

### 原来的写法

```python
dp = [-1 for i in range(amount+1)]
dp[0]=0
for i in range(1,amount+1):
    cur_min_coin = float("+inf")
    for coin in coins:
        if i-coin>=0:
            cur_min_coin=min(cur_min_coin,dp[i-coin]+1)
    dp[i] = cur_min_coin
if dp[amount]==float("+inf"):
    return -1
else:
    return dp[amount]
```

思路和复杂度 O(amount × len(coins)) 都没问题。edge case 烦人是因为初值没选好：

- **`-1` 当初值很危险**：这里没出错，只是因为每个 `dp[i]` 都被 `cur_min_coin` 整个覆盖了。一旦改成就地 `min` 更新，`-1` 就会被 `min` 选中，`dp[i-coin]+1` 还会把它变成 0。
- **改用很大的值当哨兵**：`min` 会自动绕开它，`cur_min_coin` 和 `if` 都可以删掉。
- **贪心为什么不行**：`6, [5,3,2]` 先拿 5，剩 1 凑不出来；`6, [4,3,1]` 会拿成 4+1+1，比 3+3 多一枚。

### 整理后

```python
class Solution:
    def coinChange(self, coins: list[int], amount: int) -> int:
        dp = [0] + [amount + 1] * amount
        for coin in coins:
            for i in range(coin, amount + 1):
                dp[i] = min(dp[i], dp[i - coin] + 1)
        return dp[amount] if dp[amount] <= amount else -1
```

| 改动 | 为什么 |
|---|---|
| 哨兵用 `amount + 1` | 面值最小是 1，所以合法答案最多 `amount` 枚，`amount + 1` 不可能是真答案；全程都是 int，不用混 `float("inf")` |
| coin 放外层 | `range(coin, ...)` 的起点已经保证了 `i - coin >= 0`，不用再写 `if` |
| 结尾的判断 | 删不掉：DP 内部"凑不出"要用大值表示，`min` 才能绕开；题目却要求返回 -1，最后只能转换一次。如果直接用 -1 当初值，内层循环每次都要判断，代价更大 |

### 循环顺序：coin 在外还是 index 在外

> 求最值（min/max）时两种顺序都对；求方案数时顺序会影响结果。

- **本题（求最少枚数）**：不管怎么套循环，`dp[i]` 都会和每个 `dp[i-coin]+1` 比较一遍，比较顺序不影响 `min` 的结果。
- **[518 Coin Change II](https://leetcode.com/problems/coin-change-ii/)（求组合数）**：**coin 在外**。每种硬币按固定先后加入，1+2 和 2+1 只算一次。
- **[377 Combination Sum IV](https://leetcode.com/problems/combination-sum-iv/)（求排列数）**：**index 在外**。每个金额都把所有硬币试一遍，1+2 和 2+1 算两种。

统一写 coin 在外：518 可以直接照搬，只有 377 需要特意换顺序（排列 → 金额在外）。相关范式见 [1d-dp](../paradigms/1d-dp.md)。
