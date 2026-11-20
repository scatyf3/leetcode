# 2250. Count Number of Rectangles Containing Each Point

OA 原题 3(source + distance 找范围内的 target)的同类题,见 [oa-recap.md](../notes/oa-recap.md)。

---

## 思路是怎么走过来的(原话)

1. naive: 遍历rectangles，遍历points；排序rectangles，对每个点讨论落在哪个环里 —— 我说的是optimal的思路吗
2. 那就是分别对x和y算落在哪个地带，然后merge在一起？
3. 对y分桶，对x二分吗

### 试错 1:排序以后不是「环」

矩形都从原点出发,但宽的不一定高,谁也不包含谁:

| 点 | `[[3,1], [1,3]]` 里哪些矩形包含它 |
|---|---|
| (1, 1) | 两个都包含 |
| (2, 1) | 只有 [3, 1] |
| (1, 2) | 只有 [1, 3] |
| (2, 2) | 都不包含 |

按 l 排序后,「l ≥ x」确实是一段后缀,但里面还得再筛「h ≥ y」。**两个维度都要满足**,只排一维不够。

### 试错 2:两维各算再 merge

A = {l ≥ x}、B = {h ≥ y} 各自二分很快,但要的是 |A ∩ B|:求交集一个点 O(n),总共 O(n·m),和暴力一样。
只拿到 |A|、|B| 两个数也凑不出交集(容斥要 |A ∪ B|,一样难算)。

> 两维不能各算再合并,要**套起来**:先用一维缩小范围,在范围里对另一维二分。

### 解法:按 h 分桶,桶内对 l 二分

数据范围里 h、y ≤ 100,l、x ≤ 1e9。小的那一维直接枚举:

- 预处理:`buckets[h]` 放所有高度恰好是 h 的矩形的 l,每个桶排序
- 查询 (x, y):遍历 h = y … 100 的桶(这一维已经满足),每个桶里二分数 l ≥ x 的个数,加起来
- 复杂度:O(n log n + m · 100 · log n)

```python
from bisect import bisect_left

class Solution:
    def countRectangles(self, rectangles: list[list[int]], points: list[list[int]]) -> list[int]:
        MAXH = 100
        buckets = [[] for _ in range(MAXH + 1)]
        for l, h in rectangles:
            buckets[h].append(l)
        for b in buckets:
            b.sort()

        ans = []
        for x, y in points:
            cnt = 0
            for h in range(y, MAXH + 1):             # 第一维:挑桶
                b = buckets[h]
                cnt += len(b) - bisect_left(b, x)    # 第二维:桶里 l >= x 的个数
            ans.append(cnt)
        return ans
```

> 二维计数:取值少的那一维**分桶枚举**,取值大的那一维**桶内排序 + 二分**。
> 两维都大就要离线排序 + 树状数组(还没写)。OA 第 3 题做完曼哈顿 u = x+y、v = x−y 变换后就是这个情况。

自测:

| rectangles | points | 答案 | 测什么 |
|---|---|---|---|
| `[[2,2]]` | `[[2,2]]` | `[1]` | 边界上算包含 → 必须 `bisect_left` |
| `[[2,2]]` | `[[3,1]]` | `[0]` | |
| `[[1,2],[2,3],[2,5]]` | `[[2,1],[1,4]]` | `[2,1]` | 题目样例 |

---

## Python 二分 API:`bisect`

更完整的介绍(和 SortedList 怎么选)见 blog [bisect 与 SortedList](../../blog/docs/python/bisect-sorted.md)。
这里只记刷题用得上的。以下 `a` 都是**升序** list,`n = len(a)`。

### 两个函数,一句话区别

```python
from bisect import bisect_left, bisect_right    # bisect 就是 bisect_right 的别名

bisect_left(a, x)     # 第一个 >= x 的位置  (x 存在时,落在最左边那个 x 上)
bisect_right(a, x)    # 第一个 >  x 的位置  (x 存在时,落在最右边那个 x 的后一位)
```

```
a      = [1, 3, 3, 3, 5]
index     0  1  2  3  4
bisect_left(a, 3)  = 1     ← 第一个 3
bisect_right(a, 3) = 4     ← 最后一个 3 的后面
```

x 不存在时两个返回值一样,都是「插进去还保持有序」的位置。

### 返回值 = 个数

返回的是**下标**,同时也是**左边有几个元素**。所以数个数不用写循环:

| 要数什么 | 写法 |
|---|---|
| `< x` 的个数 | `bisect_left(a, x)` |
| `<= x` 的个数 | `bisect_right(a, x)` |
| `>= x` 的个数 | `n - bisect_left(a, x)` ← 本题 |
| `> x` 的个数 | `n - bisect_right(a, x)` |
| 落在 `[lo, hi]` 的个数 | `bisect_right(a, hi) - bisect_left(a, lo)` |

记法:**带等号的那一侧决定用哪个**。`>= x` / `< x` 是在 x 的左边界切一刀 → left;`<= x` / `> x` 在右边界切 → right。

### 找具体的元素

| 要找 | 写法 | 越界检查 |
|---|---|---|
| x 在不在 | `i = bisect_left(a, x)` | `i < n and a[i] == x` |
| 最小的 `>= x`(后继) | `a[bisect_left(a, x)]` | `i < n` |
| 最小的 `> x` | `a[bisect_right(a, x)]` | `i < n` |
| 最大的 `<= x`(前驱) | `a[bisect_right(a, x) - 1]` | `i >= 0` ← [981](../981.%20Time%20Based%20Key-Value%20Store/note.md) 查某时刻的值 |
| 最大的 `< x` | `a[bisect_left(a, x) - 1]` | `i >= 0` |

越界检查最容易忘:x 比所有元素都大时 `bisect_left` 返回 n,直接取 `a[n]` 会 IndexError。

### 其他参数

```python
bisect_left(a, x, lo, hi)          # 只在 a[lo:hi] 里找,返回的仍是整个 a 的下标
insort(a, x)                       # 插入并保持有序。找位置 O(log n),插入 O(n)!
bisect_left(a, k, key=f)           # 3.10+:按 f(元素) 比较
```

- **`key=` 的坑**:被查的 x **不会**过 key,要自己先算好。
  `bisect_left(recs, 3, key=lambda r: r[0])` 可以;传整条记录 `(3, 'z')` 会 TypeError。
  但 `insort(..., key=f)` 会对 x 调 f —— 两个函数行为不一样。
- **`insort` 是 O(n)**:建一次、查多次用 bisect;边插边查用 `SortedList`(见上面的 blog 链接)。
- **降序 list 不支持**:要么存相反数,要么 `bisect_left(a, -x, key=lambda v: -v)`。

### 和手写二分的关系

`bisect_left(a, x)` 等价于闭区间模板 `[l, r]` 里「找第一个 >= x,`return l`」那一套
(见 blog [二分查找](../../blog/docs/paradigms/binary-search.md))。
有现成的就用库;要二分的是「答案」而不是数组(比如 69、1802),或者面试官要求手写时,再写模板。
