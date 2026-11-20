---
title: sort / sorted
status: draft
order: 7
related: [/python/list, /python/bisect-sorted, /paradigms/intervals, /paradigms/greedy]
---

# sort / sorted

## 一句话

**Timsort：先找出数据里本来就有序的段，再像归并排序那样把段两两合并。** 稳定，最坏 O(n log n)，
已经有序或者基本有序的输入接近 O(n)。

| | `a.sort()` | `sorted(it)` |
|---|---|---|
| 作用在 | 只有 `list` | 任何可迭代对象（str、dict、生成器……） |
| 结果 | **原地**改 `a`，返回 `None` | 返回**新 list**，原对象不动 |
| 额外内存 | 合并时最多 O(n) | 先拷一份 O(n)，再加合并的 O(n) |

## 底层长什么样

### 第一步：切 run

从左往右扫，找出一段段**本来就有序**的连续区间，叫 run：

- 非递减的段直接当 run。
- **严格递减**的段原地翻转成递增，再当 run。必须是严格递减：如果把相等的元素也翻转，它们的先后顺序就变了，排序就不稳定了。
- 太短的段（短于 minrun，一般是 32 到 64）用**二分插入排序**补长。小数组上插入排序比归并快。

```
输入:   [1, 4, 7, 9 | 8, 6, 2 | 3, 5, 10]
run:     ───递增───   严格递减    ──递增──
                       翻转成 [2, 6, 8]
```

### 第二步：合并 run

run 放在一个栈上，按一套规则两两合并，让每次合并的两段长度差不多（和归并排序一样，平衡才是 O(n log n)）。
合并时如果发现一边连续赢了很多次，就切换到**跳跃模式**（galloping），用指数搜索加二分一次跳过一大段，
不再一个个比。3.11 起合并顺序改用 Powersort 的规则，思路没变。

### 所以复杂度是这样来的

| 输入 | 比较次数 | 原因 |
|---|---|---|
| 已经有序 | n − 1 | 整个数组就是一个 run，扫一遍就完了 |
| 完全逆序 | n − 1 | 一个严格递减的 run，翻转一次就完了 |
| 随机 | ~n log₂ n | 退化成普通的归并 |
| 几段有序拼起来 | 介于两者之间 | run 少，合并次数就少 |

> 可以在解释器里验证：给元素类写一个带计数的 `__lt__`，排 1000 个已有序的元素只比 999 次，随机的 1000 个大约 8600 次。

## key：每个元素只算一次

```python
words.sort(key=len)                         # 按长度
points.sort(key=lambda p: p[0]**2 + p[1]**2)  # 按到原点的距离（LC 973）
intervals.sort(key=lambda x: x[0])          # 按 start（LC 56）
```

`key` 函数**每个元素只调一次**：Python 先把每个元素的 key 算好存起来，再按 key 排序。
所以 key 写得再贵也只花 n 次，不是 n log n 次。代价是多占 O(n) 内存存这些 key。

没给 key 时直接比元素本身。**list 和 tuple 按字典序比**：先比第 0 项，相等再比第 1 项……
所以 `intervals.sort()` 不写 key，效果是按 start 排、start 相同再按 end 排。

## 多关键字排序

### 方向一致：返回一个元组

```python
people.sort(key=lambda p: (p.age, p.name))     # 先按年龄，再按名字，都是升序
```

### 方向不同：数字取负

```python
pairs.sort(key=lambda p: (-p[1], p[0]))        # 第二项降序，第一项升序
```

### 方向不同、又不能取负（比如字符串）：靠稳定性排两次

**先按次要关键字排，再按主要关键字排**。第二次排序遇到主关键字相等的元素，会保持第一次排好的顺序：

```python
p = [("bob", 3), ("amy", 3), ("bob", 1), ("cat", 2)]
p.sort(key=lambda t: t[1])                     # 次要：年龄升序
p.sort(key=lambda t: t[0], reverse=True)       # 主要：名字降序
# [('cat', 2), ('bob', 1), ('bob', 3), ('amy', 3)]
```

> 多关键字排序能拆成几次单关键字排序，前提就是排序是**稳定**的。

## reverse=True 不等于排完再翻转

```python
a = [(1, 'a'), (2, 'b'), (1, 'c'), (2, 'd')]
sorted(a, key=lambda t: t[0], reverse=True)          # [(2,'b'), (2,'d'), (1,'a'), (1,'c')]
list(reversed(sorted(a, key=lambda t: t[0])))        # [(2,'d'), (2,'b'), (1,'c'), (1,'a')]
```

`reverse=True` 是按降序排，**相等的元素保持原来的先后**，仍然稳定。排完再翻转会把相等元素的顺序也翻过来。

## cmp_to_key：顺序没法写成 key 的时候

有些顺序只能两两比较才说得清。比如 LC 179 Largest Number：`a` 排在 `b` 前面，当且仅当 `a + b > b + a`。
这没法给每个数单独算一个 key，就用比较函数：

```python
from functools import cmp_to_key

def cmp(a, b):              # 返回负数：a 在前；正数：b 在前；0：相等
    if a + b > b + a: return -1
    if a + b < b + a: return 1
    return 0

nums = sorted(map(str, nums), key=cmp_to_key(cmp))
# [3, 30, 34, 5, 9] → ['9', '5', '34', '3', '30']
```

能写成 key 就写 key。`cmp_to_key` 每次比较都要调一次 Python 函数，比 key 慢。

## 复杂度

| 操作 | 复杂度 |
|---|---|
| `a.sort()` / `sorted(a)` | 最坏 O(n log n)，有序输入 O(n) |
| 额外内存 | 最多 O(n)，带 key 再加 O(n) |
| `min(a)` / `max(a)` | O(n)，只要最值就别排序 |
| `heapq.nsmallest(k, a)` | O(n log k)，只要前 k 个就别全排（见 [heapq](heapq.md)） |

## 由此而来的坑

- **`a = a.sort()`**：`sort` 原地改、返回 `None`，`a` 就变成 `None` 了。要新 list 用 `sorted`。
- **`sorted` 返回的总是 list**：`sorted("cab")` 是 `['a', 'b', 'c']`，要字符串得 `"".join(...)`（LC 49 用 `tuple(sorted(s))` 当 key）。
  `sorted(d)` 对 dict 排的是 key。
- **字符串按码位比**：`'B' < 'a'`（大写字母都排在小写前面），`'10' < '9'`（逐字符比，`'1' < '9'`）。数字字符串要先转 `int`。
- **元组里有比不了的东西**：`sorted([(1, None), (1, 2)])` 第 0 项相等就去比第 1 项，`None` 和 `int` 比较会抛 `TypeError`。
  只想按第 0 项排就写 `key=lambda t: t[0]`，相等的保持原序。
- **只按一部分排序时，相等元素的顺序是原序**：`key=lambda x: x[0]` 不会帮你按 end 排。要两项都排就返回元组。
- **`min` / `max` 遇到并列返回第一个**：`max([(1,'b'), (3,'a'), (3,'c')], key=lambda t: t[0])` 返回 `(3, 'a')`。

## 什么时候用

- **区间题先排序**：按 start 排再扫一遍合并（[LC 56](https://github.com/scatyf3/leetcode/blob/main/tracker/56.%20Merge%20Intervals/note.md)、
  [57](https://github.com/scatyf3/leetcode/blob/main/tracker/57.%20Insert%20Interval/note.md)、
  [252](https://github.com/scatyf3/leetcode/blob/main/tracker/252.%20Meeting%20Rooms/note.md)），
  按 end 排做贪心（[435](https://github.com/scatyf3/leetcode/blob/main/tracker/435.%20Non-overlapping%20Intervals/note.md)）。见 [区间](../paradigms/intervals.md)。
- **排好序再二分**：建一次、查很多次（[LC 2250](https://github.com/scatyf3/leetcode/blob/main/tracker/2250.%20Count%20Number%20of%20Rectangles%20Containing%20Each%20Point/note.md)
  桶内排序后用 bisect）。见 [bisect 与 SortedList](bisect-sorted.md)。
- **排序当规范化**：字母异位词排序后相同（[LC 49](https://github.com/scatyf3/leetcode/blob/main/tracker/49.%20Group%20Anagrams/note.md)）。
- **按位置排序再扫**：[LC 853](https://github.com/scatyf3/leetcode/blob/main/tracker/853.%20Car%20Fleet/note.md) 按位置排序，从离终点最近的车开始处理。
