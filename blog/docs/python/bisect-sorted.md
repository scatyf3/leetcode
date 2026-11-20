---
title: bisect 与 SortedList
status: draft
order: 6
related: [/structures/ordered-set, /paradigms/binary-search, /python/sort]
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

### left 和 right 差在哪

x 存在时，`bisect_left` 落在**最左边那个 x** 上，`bisect_right` 落在**最右边那个 x 的后一位**：

```
a      = [1, 3, 3, 3, 5]
index     0  1  2  3  4
bisect_left(a, 3)  = 1     ← 第一个 3
bisect_right(a, 3) = 4     ← 最后一个 3 的后面
```

x 不存在时两个返回值一样，都是「插进去还保持有序」的位置。`bisect.bisect` 就是 `bisect_right` 的别名。

### 返回值就是个数

返回的是下标，同时也是**左边有几个元素**。所以数个数不用写循环（下面 `n = len(a)`）：

| 要数什么 | 写法 |
|---|---|
| `< x` 的个数 | `bisect_left(a, x)` |
| `<= x` 的个数 | `bisect_right(a, x)` |
| `>= x` 的个数 | `n - bisect_left(a, x)`（[LC 2250](https://github.com/scatyf3/leetcode/blob/main/tracker/2250.%20Count%20Number%20of%20Rectangles%20Containing%20Each%20Point/note.md)） |
| `> x` 的个数 | `n - bisect_right(a, x)` |
| 落在 `[lo, hi]` 的个数 | `bisect_right(a, hi) - bisect_left(a, lo)` |

记法：`>= x` 和 `< x` 都是在 x 的**左边界**切一刀，用 left；`<= x` 和 `> x` 在**右边界**切，用 right。

### 找具体的元素

| 要找 | 写法 | 越界检查 |
|---|---|---|
| x 在不在 | `i = bisect_left(a, x)` | `i < n and a[i] == x` |
| 最小的 `>= x`（后继） | `a[bisect_left(a, x)]` | `i < n` |
| 最小的 `> x` | `a[bisect_right(a, x)]` | `i < n` |
| 最大的 `<= x`（前驱） | `a[bisect_right(a, x) - 1]` | `i >= 0`（[LC 981](https://github.com/scatyf3/leetcode/blob/main/tracker/981.%20Time%20Based%20Key-Value%20Store/note.md) 查某个时刻的值） |
| 最大的 `< x` | `a[bisect_left(a, x) - 1]` | `i >= 0` |

越界检查最容易忘：x 比所有元素都大时 `bisect_left` 返回 n，直接取 `a[n]` 会 `IndexError`。

### 其他参数

```python
bisect_left(a, x, lo, hi)      # 只在 a[lo:hi] 里找，返回的仍是整个 a 的下标
bisect_left(a, k, key=f)       # 3.10+：按 f(元素) 比较
```

- **`key=` 不作用在被查的 x 上**，要自己先算好：`bisect_left(recs, 3, key=lambda r: r[0])` 可以，
  传整条记录 `(3, 'z')` 会 `TypeError`。但 `insort(a, x, key=f)` **会**对 x 调 f，两个函数的行为不一样。
- **只支持升序**：降序 list 要么存相反数，要么 `bisect_left(a, -x, key=lambda v: -v)`。
- 要先排好序：见 [sort / sorted](sort.md)。

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
