---
title: Python 内置
---

# Python 内置

这一层回答两个问题：**这个 API 底下是什么结构**，以及**复杂度和坑是从那个结构里来的**。
L2 那张推导图上的每个概念，在 Python 里落到哪：

| 概念（L2） | Python | 底层 |
|---|---|---|
| 数组 | `list` | 指针的动态数组 |
| 栈 | `list` 的 `append` / `pop` | 同上，只碰尾巴 |
| 队列 / 双端队列 | `collections.deque` | 定长块组成的双向链表 |
| 哈希表 / 集合 | `dict` / `set` | 开放寻址哈希表 |
| 堆 | `heapq` | 普通 `list` 上的一组函数 |
| 有序集合 | 没有内置：`bisect` + `list`，或 `sortedcontainers.SortedList` | 有序数组 / 分块有序数组 |
| 字符串 | `str` | 不可变的定长码位数组 |

语法层面的坑另有一套闪卡在 [tracker/syntax/](https://github.com/scatyf3/leetcode/tree/main/tracker/syntax)，
看板里按 FSRS 抽着复习；这里讲的是坑**为什么**会在那儿。

<LayerIndex dir="python" />
