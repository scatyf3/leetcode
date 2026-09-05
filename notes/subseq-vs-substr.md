# 子串 / 子数组 / 子序列:一个词决定解法族

栽过一次:把 LC 300 `lengthOfLIS` 当滑动窗口做,四问决策清单从头到尾走了一遍,
但清单的**前提**不成立 —— 那题根本不是连续区间问题。一个词看错,后面全白搭。

配套:[sliding-window-template.md](sliding-window-template.md)(连续区间的骨架)、[../paradigms/1d-dp.md](../paradigms/1d-dp.md)(可跳的那一族)

---

## 三个词是术语,不是每题临时约定

题面**不写定义也不算漏写**,就像它不会定义什么叫 "array"。看到就直接分流。

| 英文 | 中文 | 连续? | 保序? | 解法族 |
|---|---|---|---|---|
| `substring` | 子串 | **是** | 是 | 滑窗 / 中心扩展 / 双指针 |
| `subarray` | 子数组 | **是** | 是 | 滑窗 / 前缀和 / Kadane |
| `subsequence` | 子序列 | **否**(可删中间) | 是 | **DP** / 贪心+二分 |
| `subset` | 子集 | 否 | 否(顺序无关) | 回溯 / 位运算 / 背包 |

> `sequence` 强调的是**顺序**,不是**相邻** —— 英文其实比中文好认。
> 中文「子序列」和「子数组」只差一个字,是读题第一杀手。

## 同一个性质的「连续版 vs 可跳版」

出题人很爱成对出这种题,只换一个词,解法完全不同:

| 性质 | 连续版 | 可跳版 |
|---|---|---|
| 回文 | **5** 最长回文子串 / **647** 回文子串计数 | **516** 最长回文子序列 |
| 递增 | **674** 最长连续递增序列 | **300** 最长上升子序列 |
| 公共 | **718** 最长重复子数组 | **1143** 最长公共子序列 |
| 和/积 | **209** 最短子数组 / **152** 最大乘积子数组 | 背包类(494 等) |

同一个输入,两个答案是实质不同的:

    nums = [10,9,2,5,3,7,101,18]
    300 最长上升子"序列"(可跳)  = 4   [2,3,7,101], 跳过了下标 3 的 5
    674 最长连续递增"子数组"    = 3   [3,7,101]

## 三个坑

### 坑 1:"continuous subsequence" —— 用了 subsequence 但指连续

LC 674 标题是 *Longest **Continuous** Increasing Subsequence*。
`continuous` 这个修饰词会**推翻** `subsequence` 的默认含义。
所以规矩是:**看有没有修饰词,修饰词优先于词本身。**

### 坑 2:`consecutive` 可能指「值连续」而不是「位置连续」

LC 128 *Longest **Consecutive** Sequence*:

    Input: nums = [100,4,200,1,3,2]   (unsorted)
    Output: 4    Explanation: [1,2,3,4]

这里的 consecutive 指**数值上连着**(1,2,3,4),和它们在数组里的位置、顺序都没关系。
所以 128 既不是滑窗也不是 DP,而是哈希集合。**别看到 consecutive 就以为是连续区间。**

### 坑 3:题面正文可能压根没定义

LC 300 的正文只有一句 "return the length of the longest strictly increasing subsequence",
底下没有那句常见的 "A subsequence is a sequence that can be derived by deleting some or no elements…"。
定死它的是 **Example 1 的 Explanation**:

    Input:  [10,9,2,5,3,7,101,18]
    Output: 4
    Explanation: The longest increasing subsequence is [2,3,7,101]

`[2,3,7,101]` 在原数组里不连续 -> 可跳。**具体的例子比定义句更硬。**

## 所以读题顺序改成

    标题 -> Example 1 的 Explanation -> 正文 -> Constraints

Explanation 里那个具体答案能当场排除掉一半误读。花两秒看一眼「例子里的答案在原输入里连不连续」,
比读三遍正文管用。

## 动手前的自检

1. 题面(含标题)里的那个 sub* 词是哪一个?有没有 `continuous` / `contiguous` 之类的修饰词?
2. Example 的答案,在原输入里**连续吗**?
3. 如果是 `consecutive`,它说的是**位置**连续还是**数值**连续?

三问都答完再决定用哪个模板。答不上来就别开始敲。
