---
title: 有序集合
status: draft
order: 6
alias: []
related: [/python/bisect-sorted, /structures/heap, /paradigms/heap]
---

# 有序集合

堆只保证「父 ≤ 子」，所以它只知道最小的是谁；有序集合把所有元素**排成一列**，于是能问的多了：
比 x 大的最小那个是谁（前驱 / 后继）、第 k 个是谁、删掉任意一个 x —— 而且插入、删除、这些查询都还是 O(log n)。
这就是 [概念数据结构](index.md) 推导图里「偏序 → 全序」那一步。

```
堆:        只有堆顶是确定的        → 最小是谁
有序集合:  1  3  4  7  9  12      → 比 5 大的最小是 7；第 3 个是 4；删掉 9
```

C++ 是 `std::set`，Java 是 `TreeMap` / `TreeSet`，底下是平衡二叉搜索树。**Python 没有内置。**

## Python 里怎么凑

| 写法 | 查询 | 插入 / 删除 | 什么时候用 |
|---|---|---|---|
| 有序 `list` + `bisect` | O(log n) | **O(n)**，`list.insert` 要挪元素 | 建一次、查很多次 |
| `sortedcontainers.SortedList` | O(log n) | 接近 O(log n) | 又插又删又查。LeetCode 上能 import，别的判题环境和白板面试不一定有 |
| 堆 + 懒删除 | 只有最值 | O(log n) 均摊 | 只要最值，但要删任意元素 |

API 和 `SortedList` 怎么实现的见 [bisect 与 SortedList](../python/bisect-sorted.md)。

第一行的 O(n) 我在 295 上撞过：有序数组 + 二分插入，以为是 O(log n)，其实二分找位置 O(log n)，挪元素 O(n)，
瓶颈在修复不在查找（[295 sol.py](https://github.com/scatyf3/leetcode/blob/main/tracker/295.%20Find%20Median%20from%20Data%20Stream/sol.py)）。
295 最后用的是对顶堆，因为中位数只要中间那一刀，用不着全序 —— 见 [堆的用法](../paradigms/heap.md) §3。

懒删除：要删的值先记在一个计数 dict 里，不动堆；等它浮到堆顶、被 `h[0]` 看到时，再真的弹掉。
堆里会多躺一些「已删除」的元素，但每个最多被弹一次，均摊还是 O(log n)。

## 什么时候真的需要它

先问 [128 的 note](https://github.com/scatyf3/leetcode/blob/main/tracker/128.%20Longest%20Consecutive%20Sequence/note.md)
末尾那句：**我到底需要多少有序？** 只要最值用堆，只要相邻关系用 set。以下情况才是真要全序：

- **要删任意元素，同时还要中位数 / 第 k 个**：480 Sliding Window Median，窗口右移时左边那个数要删掉。
  `SortedList` 直接做；不用它就是对顶堆 + 懒删除。
- **要问「离 x 最近的那个」**：220 Contains Duplicate III，窗口里有没有落在 `[x - t, x + t]` 的数，就是问「`>= x - t` 的最小那个」是不是 `<= x + t`；
  729 My Calendar I，新区间要和前驱、后继两个已有区间比是否重叠。

这几道仓库里都还没做。
