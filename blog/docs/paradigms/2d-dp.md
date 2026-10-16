---
title: 二维 DP
status: draft
order: 12
alias: []
related: [/paradigms/1d-dp, /paradigms/two-pointer]
---

# 二维 DP

「二维」说的是**下标有两个**，不是每格存两个数（这条见 [1d-dp.md](1d-dp.md) §3）。
两个下标的来路只有三种：网格的行和列（62 / 64）、两个串各一个前缀（1143 / 72）、同一个串的左右端点（5 / 647）。
画出来都是一张表，每一格只看旁边几格。所以动手前只要回答两件事：

1. `dp[i][j]` 是「前 i 个和前 j 个」、「以 i、j 结尾」，还是「`s[i..j]` 这一段」？
2. 它看哪几个邻居？—— 这决定了填表顺序。

## 1. 先定 `dp[i][j]` 是什么

| 口径 | `dp[i][j]` | 表多大 | 答案在哪 | 例 |
|---|---|---|---|---|
| 网格 | 走到 `(i, j)` | `m × n`，表就是网格 | `dp[m-1][n-1]` | 62 / 64 |
| 两个前缀 | `text1[:i]` 和 `text2[:j]` | `(m+1) × (n+1)`，第 0 行 / 列是空串 | `dp[m][n]` | 1143 / 72 |
| 以 i、j 结尾 | 恰好以 `text1[i-1]`、`text2[j-1]` 结尾 | `(m+1) × (n+1)` | 整张表的 max | 718 |
| 区间 | `s[i..j]` 这一段 | `n × n`，只用上三角 | 看题 | 5 / 647 / 516 |

选哪个口径，1143 的 note 里有一句判据：**转移过程中哪些量会变，就用哪些量作下标。**
LCS 只从末尾削字符，从 `(:m, :n)` 出发怎么削都还是两个前缀，左端点永远是 0，不用占维度；
516 最长回文子序列要两头一起往里削，左端点会变，才需要区间。

「前缀」和「以 i 结尾」的选法，和 [1d-dp.md](1d-dp.md) §2 的口径 A / B 是同一件事搬到二维：
子序列能跳字符 → 前缀，不等时 `max` 跳过一边；子串必须连续 → 以 i、j 结尾，不等时归 0。
三个词怎么认见 [subseq-vs-substr](https://github.com/scatyf3/leetcode/blob/main/tracker/notes/subseq-vs-substr.md)。

## 2. 依赖方向决定填表顺序

```
  网格 / 两个前缀：看左、上、左上          区间：看左下（516 还看左、下）

         j-1      j                             j-1      j
  i-1   [↘]      [↓]                     i     [→]    [i][j]
  i     [→]    [i][j]                    i+1   [↗]      [↑]

  行优先、两层正序就行                     i 倒序，或按区间长度递增
```

规则只有一条：**被依赖的格子必须先算完。** 左、上、左上都在「前面的行或本行前面」，两层正序天然满足。
区间 DP 的 `f[i][j]` 要 `f[i+1][j-1]`，在**下一行**，i 在外层正序会读到还没算的 `False`
（5 的区间 DP 版在 `"aaaa"` 上只报到长度 3，整串 `f[0][3]` 查 `f[1][2]` 时它还没算）。
这类题的真考点是遍历顺序，不是转移方程。

## 3. 网格：62 / 64

表就是网格本身，每格只能从上或左来。唯一要想的是**首行首列**：它们只有一条路，必须单独初始化。

- **64**：`dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]`，首行首列是**前缀累加**，不能当 0
- **62**：`dp[i][j] = dp[i-1][j] + dp[i][j-1]`，首行首列全是 1。那张表是斜放的杨辉三角，
  所以也等于 `math.comb(m + n - 2, m - 1)`：m+n-2 步里挑 m-1 步往下

## 4. 两个串：1143 / 72

两题骨架一样：比较两个前缀的**末尾字符**，相等就一起往前一格（左上），不等就看削哪一边。

```python
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        m, n = len(text1), len(text2)
        # dp[i][j]: text1 前 i 个字符 和 text2 前 j 个字符 的 LCS 长度
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i][j-1], dp[i-1][j])

        return dp[m][n]
```

72 只多了两处：不等时三种操作取 min + 1，以及边界不是 0。

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        # dp[i][j]: 把 word1[:i] 变成 word2[:j] 的最少操作数
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i          # 全删
        for j in range(n + 1):
            dp[0][j] = j          # 全插

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],     # 删除 word1[i-1]
                        dp[i][j-1],     # 插入 word2[j-1]
                        dp[i-1][j-1],   # 替换 word1[i-1] → word2[j-1]
                    )

        return dp[m][n]
```

三种操作对应哪个邻居，记一句：**哪边的字符被消耗，哪边的下标就减 1。**
插入的那个字符是拿来配 `word2[j-1]` 的，消耗的是 word2，所以是 `j-1`；删除消耗 word1 的原始字符，所以是 `i-1`。

`"horse" → "ros"` 的表（行是 word1 的前缀，列是 word2 的前缀）：

```
      ""  r  o  s
""     0  1  2  3
 h     1  1  2  3
 o     2  2  1  2
 r     3  2  2  2
 s     4  3  3  2
 e     5  4  4  3      ← 答案 dp[5][3] = 3
```

第 0 行、第 0 列就是那两行边界。LCS 里空串对应 0，这里空串要全插 / 全删。

## 5. 区间：5 / 647

回文子串这两题，区间 DP（`f[i][j]` = `s[i..j]` 是否回文）能做，但**不是首选**：中心扩展同样 O(n²)、只要 O(1) 空间。
区间 DP 值得写一遍，是因为它的状态和「按长度递增」的填表顺序能迁到 516 / 1312 这些子序列题，那里中心扩展彻底失效。

两套骨架、判定型和长度型的区别都在
[palindrome-family](https://github.com/scatyf3/leetcode/blob/main/tracker/notes/palindrome-family.md)，这里只记区间 DP 自己的两个坑：
按长度递增（§2），以及 `length == 2` 时内部区间为空、要短路掉，不能去查 `f[i+1][j-1]`。

## 6. 滚动成一行

前缀 / 网格类每格只看上一行和本行，所以一行就够（判据见 [1d-dp.md](1d-dp.md) §5）。
坑在左上角：从左往右覆盖时，`dp[i-1][j-1]` 在算到 `j` 之前已经被本行的 `dp[i][j-1]` 盖掉了，要先用一个变量存下来：

```python
def lcs_one_row(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    row = [0] * (n + 1)              # 进入第 i 行前，row[j] = dp[i-1][j]
    for i in range(1, m + 1):
        diag = 0                     # dp[i-1][0]
        for j in range(1, n + 1):
            up = row[j]              # dp[i-1][j]，马上要被覆盖
            if text1[i-1] == text2[j-1]:
                row[j] = diag + 1
            else:
                row[j] = max(row[j-1], up)   # row[j-1] 已经是本行的 dp[i][j-1]
            diag = up                # 下一格的左上 = 这一格的上
    return row[n]
```

62 不需要这个变量（`row[j] += row[j-1]`），因为它根本不看左上。

## 7. 坑

- **删 / 插的注释写反**（72）：代码是对的（三项取 min，顺序无关），但标签反了 —— 插入是 `dp[i][j-1]`，删除是 `dp[i-1][j]`
- **首行首列当 0**（64）：只有一条路，要单独做前缀累加
- **下标是前缀长度**（1143 / 72）：取字符写 `text1[i-1]`，不是 `text1[i]`
- **区间 DP 按 i 正序填**（5 / 647）：读到没算的格子，`"aaaa"` 只报到 3；`length == 2` 不查表
- **组合数先除再乘**（62）：`res = res * (N-k+i) // i` 要先乘再整除，`7 // 2` 就丢了余数
- **把 718 当 1143 写**：子串不等时归 0、答案取整表 max；子序列不等时取 max、答案在 `dp[m][n]`
