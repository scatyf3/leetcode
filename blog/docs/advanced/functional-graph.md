---
title: 函数图
status: todo
order: 3
alias: []
related: [/paradigms/dfs, /structures/graph]
---

# 函数图

## 一句话

每个点恰好一条出边。从任意一个点一直往下走，最后一定会走进一个环。

## 怎么认出这类题

输入是一个数组 `edges[i]` / `favorite[i]` / `receiver[i]`，意思是点 i 指向另一个点。

建在 L3 的：[DFS](../paradigms/dfs) · [图](../structures/graph)

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| [2360. Longest Cycle in a Graph](https://leetcode.com/problems/longest-cycle-in-a-graph/) | 函数图入门：找环 |
| [2876. Count Visited Nodes in a Directed Graph](https://leetcode.com/problems/count-visited-nodes-in-a-directed-graph/) | 每个点出发能走到几个不同的点 |
| **[2127. Maximum Employees to Be Invited to a Meeting](https://leetcode.com/problems/maximum-employees-to-be-invited-to-a-meeting/)** | 环的大小不同，答案的形状也不同 |
| [2836. Maximize Value of Function in a Ball Passing Game](https://leetcode.com/problems/maximize-value-of-function-in-a-ball-passing-game/) | k ≤ 10¹⁰：先看数据范围 |

## 模板

> 还没做。先做 **2127**，做完再写模板（只留一套写法）。

## 栽过的坑

只收自己真栽过的。
