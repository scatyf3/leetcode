# 1143. Longest Common Subsequence

我对这个2d dp的建模很疑惑，为啥`dp[i][j]: text1 前 i 个字符 和 text2 前 j 个字符 的 LCS 长度`，而不是用切片语义建模？

---

### 「前 i 个」其实就是切片

`dp[i][j] = LCS(text1[:i], text2[:j])`，「前 i 个」和切片 `text1[:i]` 是同一个东西，i 就是右端点（开区间）。所以取字符要写 `text1[i-1]`。

如果说的是一般切片 `text1[a:b]`、`text2[c:d]`，也能定义，但没必要：**转移只从末尾削字符**

- 末尾相等：`(:i, :j)` → `(:i-1, :j-1)`
- 末尾不等：→ `(:i-1, :j)` 或 `(:i, :j-1)`

从 `(:m, :n)` 出发，怎么削都还是「两个前缀」，左端点永远是 0，不用占维度。硬加就成了 `dp[a][b][c][d]`，O(n⁴) 状态大部分根本到不了。

> 转移过程中哪些量会变，就用哪些量作下标。这里只有两个右端点在变 → 二维。

对照：[516 Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/) 要同时比较**两端**，转移会两头一起往里削，左端点会变 → 区间 DP `s[i:j]`。

另外也可以写后缀版 `dp[i][j] = LCS(text1[i:], text2[j:])`，完全等价，只是循环倒着跑。固定用前缀版。

### 为啥不考虑左端点

担心的情况：LCS 不一定从头开始，比如 `"xxabc"` / `"abc"`，LCS 在 text1 里从下标 2 开始。

但子序列**允许跳过字符**，前缀 `text1[:5]` 已经包含了「前面的 `xx` 不用」这种选法。跳过的动作就是不等时那一支 `max(dp[i-1][j], dp[i][j-1])`。往回推遇到 `'x'` 对不上，就走这一支扔掉，所以起点是递推时自动决定的。

和最长公共**子串**（[718](https://leetcode.com/problems/maximum-length-of-repeated-subarray/)）对比：

| | LCS（子序列） | 最长公共子串 |
|---|---|---|
| 能否跳字符 | 能 | 不能，必须连续 |
| 状态 | 两个前缀的 LCS | **恰好以** `i-1`、`j-1` 结尾的公共子串长度 |
| 不等时 | `max(左, 上)`，跳过一个 | `0`，连续性断了 |
| 答案 | `dp[m][n]` | 整张表的 max |

> 允许跳过 → 前缀；必须连续 → 「以 i 结尾」。和 [1d-dp](../paradigms/1d-dp.md) 第 2 节的口径 A / B 是同一件事，搬到了二维。

### 两个序列的 DP 通用套路

输入是两个序列、要比较或匹配 → `dp[i][j]` 表示「第一个的前 i 个 × 第二个的前 j 个」，表开 `(m+1) × (n+1)`，第 0 行 / 第 0 列是空串边界。同类题：[72 Edit Distance](../72.%20Edit%20Distance/note.md)、97 Interleaving String、115 Distinct Subsequences。

每个格子只依赖上一行和当前行，所以可以压成一维。但左上角 `dp[i-1][j-1]` 会被覆盖，要先用一个变量存下来。
