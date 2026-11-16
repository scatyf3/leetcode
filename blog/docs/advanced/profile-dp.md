---
title: 铺砖 / 轮廓线 DP
status: todo
order: 7
alias: []
parent: bitmask-dp
related: [/paradigms/2d-dp]
---

# 铺砖 / 轮廓线 DP

## 一句话

网格有一维很小，就沿着另一维一列一列（或一格一格）推进，把交界处的状态压起来。

## 怎么认出这类题

铺砖、涂色这类网格题，其中一维 ≤ 5 左右。

建在 L3 的：[状压 DP](./bitmask-dp) · [二维 DP](../paradigms/2d-dp)

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| [790. Domino and Tromino Tiling](https://leetcode.com/problems/domino-and-tromino-tiling/) | 先手推转移 |
| [1411. Number of Ways to Paint N × 3 Grid](https://leetcode.com/problems/number-of-ways-to-paint-n-3-grid/) | 先手推转移 |
| **[1931. Painting a Grid With Three Different Colors](https://leetcode.com/problems/painting-a-grid-with-three-different-colors/)** | 按列压状态 |
| [1659. Maximize Grid Happiness](https://leetcode.com/problems/maximize-grid-happiness/) | 逐格轮廓线 |

## 模板

> 还没做。先做 **1931**，做完再写模板（只留一套写法）。

## 栽过的坑

只收自己真栽过的。
