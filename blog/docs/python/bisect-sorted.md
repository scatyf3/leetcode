---
title: bisect 与 SortedList
status: draft
order: 6
related: [/structures/ordered-set, /paradigms/binary-search]
---

# bisect 与 SortedList

## 一句话

Python **没有内置的有序集合**（C++ 的 `set`、Java 的 `TreeMap`）。
只查不改用 `bisect` 在有序 list 上二分；又要查又要插删，用第三方的 `sortedcontainers.SortedList`。

## bisect：有序数组上的二分

`bisect` 只是二分查找函数，底下还是普通 `list`：

| 操作 | 复杂度 | |
|---|---|---|
| `bisect_left(a, x)` | O(log n) | 第一个 `>= x` 的位置 |
| `bisect_right(a, x)` | O(log n) | 第一个 `> x` 的位置 |
| `insort(a, x)` | **O(n)** | 找位置 O(log n)，但 `list.insert` 要挪元素 |

所以 `bisect` 适合「建一次、查很多次」（LC 981 每个 key 下的时间戳本来就递增，直接 `append` + 二分）。
一边插一边查的话，`insort` 的 O(n) 会把整体拖成 O(n²)。

3.10 起 `bisect` 支持 `key=`，但**被查的 `x` 不过 key**，要自己先算好：`bisect_left(a, key(x), key=key)`。

## SortedList：分块有序数组

把元素切成很多段有序的小 list（每段约一千个），外加一层索引。插删只挪一小段，
实际表现接近 O(log n)，常数比平衡树小。LeetCode 的环境里装了它。

```python
from sortedcontainers import SortedList
sl = SortedList()
sl.add(x)                  # 插入
sl.remove(x)               # 不存在会抛 ValueError；discard 不抛
sl.bisect_left(x)          # 和 bisect 同义
sl[0], sl[-1]              # 最小、最大
sl[sl.bisect_right(x)]     # 严格大于 x 的最小值（先判越界）
```

## 和堆怎么选

只要最值 → [heapq](heapq.md)，更快更省。要「比 x 大的最小那个」、要删任意元素、要第 k 个 → `SortedList`。
这正是 L2 推导图里「偏序 → 全序」那一步：多维护了全序，就多了这些查询。

## 和手写二分的关系

刷题时二分只写闭区间那一套（见 [二分查找](../paradigms/binary-search.md)）。
`bisect_left` 的语义等价于闭区间模板里「找第一个 `>= x`」，能直接用库就用库，面试官要手写再写模板。
