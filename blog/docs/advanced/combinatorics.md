---
title: 组合计数
status: todo
order: 2
alias: []
related: [/paradigms/1d-dp, /advanced/modular]
---

# 组合计数

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

## 模板

> 还没做。先做 **2400**，做完再写模板（只留一套写法）。

## 栽过的坑

只收自己真栽过的。
