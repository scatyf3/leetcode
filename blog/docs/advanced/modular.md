---
title: 快速幂与取模
status: todo
order: 1
alias: []
related: [/paradigms/bit-manipulation, /paradigms/recursion]
---

# 快速幂与取模

## 一句话

答案要对 1e9+7 取模时，加、减、乘随时取模，除法要换成乘逆元；指数大到 10⁹ 以上，用快速幂。

## 怎么认出这类题

题目说「返回结果对 10⁹ + 7 取模」；或者幂次、指数本身非常大。

建在 L3 的：[位运算](../paradigms/bit-manipulation)（迭代版按二进制位走）· [递归](../paradigms/recursion)（分治版每层规模减半）

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| [50. Pow(x, n)](https://leetcode.com/problems/powx-n/) | 前置题，不在 ACM 单里：快速幂模板 + 负指数 |
| **[372. Super Pow](https://leetcode.com/problems/super-pow/)** | 快速幂，指数很大时取模 |

## 模板

> 还没做。先做 **372**，做完再写模板（只留一套写法）。

## 栽过的坑

只收自己真栽过的。
