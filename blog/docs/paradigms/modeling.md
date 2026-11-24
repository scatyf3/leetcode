---
title: 建模
status: draft
order: 23
alias: []
related: [/paradigms/binary-search, /paradigms/hash, /paradigms/greedy, /advanced/graph-modeling]
---

# 建模：先翻译，再套路

这一层的其他页面讲的是**套路本身**：认出是二分、滑窗、DP 之后怎么写。这一页讲的是**认出来之前那一步**：
题面是一个故事，要先把它翻译成一个抽象问题，套路才用得上。

```
题面（故事）  →  抽象问题  →  套用工具
              ↑ 建模          ↑ 熟练度
```

- **Hot 100** 基本跳过了第一层：题面直接说「在链表上做什么」「在数组里找什么」，练的是第二层。
- **OA 和真实问题**难在第一层：basetime、版本存储、source 和 target，要自己翻译成 CAS、树上覆盖、排序后查询。
  翻译完之后用的还是 Hot 100 里那些工具。

> Hot 100 没有白练，它提供的是零件。OA 多考的是把零件对上号的那一步。

这一步需要一些经验，但常见的翻译方式数量有限。与其靠刷题去碰，不如每道题都显式问自己下面几个问题。

L4 的 [建图](../advanced/graph-modeling.md) 是这一页的一个特例：题面里没有图，要自己决定谁是点、谁是边。

## SOP

**写代码之前，先在 note 里写一行「抽象成：___」。** 写不出来，说明建模还没想清楚，这时候写代码就会一直补边界。

1. **暴力解是什么，复杂度多少，卡在哪？**（§1）瓶颈明确了，后面几问都是在消除它。
2. **答案由谁决定？就遍历谁。**（§2）
3. **两两之间的关系，能不能拆成每个元素各算一个值？**（§3）
4. **有没有一个集合可以先排序，让另一个集合来查？**（§4）
5. **去掉故事之后，这是哪道做过的题？**（§5）

写出来的那一行长这样：

| 题 | 抽象成 |
|---|---|
| 1131 | 每个下标算一个 v，求 `max(v[i] - v[j])` |
| 475 | 对每个 house 求最近 heater 的距离，再取 max |
| OA 第 1 题 | 带版本号的条件写入（CAS） |

## 1. 先写暴力，找瓶颈

| 题 | 暴力 | 卡在哪 | 怎么消掉 |
|---|---|---|---|
| [1131](https://github.com/scatyf3/leetcode/blob/main/tracker/1131.%20Maximum%20of%20Absolute%20Value%20Expression/note.md) | 枚举所有 (i, j)，O(n²) | n ≤ 4×10⁴，两两枚举太多 | 拆成单点的值（§3） |
| [475](https://github.com/scatyf3/leetcode/blob/main/tracker/475.%20Heaters/note.md) | 每个 house 扫一遍所有 heater，O(m·n) | 每次都线性找最近的 | heaters 排序后二分（§4） |

暴力解还有一个用处：拿来对拍。1131、475 最后的版本都是和暴力对拍几千组之后才确认的。

## 2. 答案由谁决定，就遍历谁

475 第一版是从 heater 的角度想的：算相邻 heater 之间空隙的一半，再加上头尾两段。
这样补了好几轮边界都补不完，每补一个都还有新的反例：

| 输入（houses, heaters） | 期望 | 从 heater 角度算出来 | 为什么错 |
|---|---|---|---|
| `[1]`, `[1, 10]` | 0 | 4 | 空隙里没有 house，也被算进去了 |
| `[2]`, `[1, 10]` | 1 | 4 | 空隙里的 house 不在正中间 |
| `[5]`, `[1, 5]` | 0 | 4 | 第一个 heater 在第一个 house 左边，多算了一段 |

根源是：**半个空隙算的是「如果有 house 在最坏的位置」，题目问的是「实际的 house 在哪」**。
只看 heater 的信息，是算不出后者的。

题目要的是「每个 house 都被覆盖」，半径由**最难覆盖的那个 house** 决定，所以遍历 house，heater 只是被查找的对象。
换过来之后，上面三类反例都不会出现，剩下的边界只有「这个 house 左边或右边没有 heater」。

> **答案由谁决定，就遍历谁。** 打个比方：路由器的信号只要覆盖到有人的地方，空房间不用管。

## 3. 两两关系拆成单点的值

看到「在所有 (i, j) 对里求 max / min」，先试着把式子拆成 `f(i) - f(j)` 或 `f(i) + g(j)`。
拆开之后，每个下标只算一个值，配对交给一个变量：

- 没有先后限制：`max(f) - min(f)`
- 要求 i > j：从左往右扫，**枚举右，维护左**，和 121 买卖股票一样（同一个思路在 [哈希](hash.md) 里是「把左边的配对特征先存进表」）

挡住拆分的，常常是绝对值。1131 的做法是**枚举符号去掉绝对值**：

```
|a| + |b| = max(a+b, a-b, -a+b, -a-b)
```

猜对的那组正好等于真实值，猜错的只会偏小，所以对所有猜法取 max 一定正确。
每组符号下式子都能写成 `v[i] - v[j]`，`v[k] = s1·arr1[k] + s2·arr2[k] + k` 只依赖一个下标。

| 题 | 式子 | 拆成 |
|---|---|---|
| [1014. Best Sightseeing Pair](https://leetcode.com/problems/best-sightseeing-pair/) | `values[i] + values[j] + i - j` | `(values[i] - i) + (values[j] + j)`，没有绝对值，热身 |
| [1131](https://github.com/scatyf3/leetcode/blob/main/tracker/1131.%20Maximum%20of%20Absolute%20Value%20Expression/note.md) | 三项绝对值相加 | 固定 `\|i-j\|` 的符号，枚举另外两项共 4 组 |

二维曼哈顿距离就是这个特例：`|x1-x2| + |y1-y2| = max(|u1-u2|, |v1-v2|)`，其中 `u = x+y`，`v = x-y`。

475 也是同一个结构：每个 house 先算出自己的最近距离，再在所有 house 上取 max。

## 4. 一个集合排序，另一个来查

Hot 100 的二分题（35、704、33、153）是「在一个数组上找东西」，二分就是题目本身。
OA 更常见的是**两个集合**：一堆数据，一堆查询。暴力 O(m·n)，把数据那边排序，每个查询二分一次，降到 O((m+n) log n)。

二分在这里只是一个零件。[35 Search Insert Position](https://github.com/scatyf3/leetcode/blob/main/tracker/35.%20Search%20Insert%20Position/note.md) 求的插入位，
就是 `bisect_left` 的返回值，475 相当于把 35 当零件用。

插入位 `i` 两侧的邻居各自可能不存在，这是这类题固定要处理的边界：

```python
i = bisect_left(data, q)       # 第一个 >= q 的下标，范围 0..len(data)
if i < len(data): ...          # 右边有
if i > 0: ...                  # 左边有
```

两个 `if` 各自独立判断，不要写成 `if 没越界 / else`。
也不要省掉 `i > 0`：Python 里 `data[-1]` 不报错，会悄悄拿到最后一个元素。

| 题 | 数据 | 查询 |
|---|---|---|
| [475](https://github.com/scatyf3/leetcode/blob/main/tracker/475.%20Heaters/note.md) | heaters | 每个 house 找最近的 heater |
| [2250](https://github.com/scatyf3/leetcode/blob/main/tracker/2250.%20Count%20Number%20of%20Rectangles%20Containing%20Each%20Point/note.md) | 矩形 | 二维：一维排序，另一维二分 |
| [981](https://github.com/scatyf3/leetcode/blob/main/tracker/981.%20Time%20Based%20Key-Value%20Store/note.md) | 每个 key 的历史版本 | 查某个时刻的值 |

## 5. 去掉故事，认出做过的题

一次 OA 的三道题，LeetCode 上都没有原题，但翻译之后都是做过的题（详见 [OA 复盘](https://github.com/scatyf3/leetcode/blob/main/tracker/notes/oa-recap.md)）：

| 题面 | 翻译成 | 落到 |
|---|---|---|
| key、value、basetime，对比上一次修改时间 | 乐观并发控制：上次修改时间 ≤ basetime 才允许写 | 981、1146 的版本号 + 二分 |
| 版本存储，每个版本都要在 cost ≤ t 内重建 | 链上就是区间覆盖贪心，树上就是自底向上覆盖 | [968](https://github.com/scatyf3/leetcode/blob/main/tracker/968.%20Binary%20Tree%20Cameras/note.md)、45 |
| 若干 source + distance，找能到达的 target | 曼哈顿距离转 45°，菱形变成矩形，再做范围查询 | 1131 的变换 + 2250 |

第 3 行同时用到了 §3 和 §4：`u = x+y`、`v = x−y` 之后，source 能到达的范围是 `[u−d, u+d] × [v−d, v+d]`，
变成了 2250 那种矩形查询。注意 1131 用这个变换是为了求**最大距离**，这里是为了**把范围变成矩形**。
如果题目是欧氏距离，这条路就走不通了。

## 栽过的坑

- **1131 pass1：先选工具再建模。** 两个数组各自 `sort`，注释写着 `# some binary search`。
  sort 把 `(arr1[i], arr2[i], i)` 这个三元组拆散了，算的是另一个问题。题里也没有任何东西需要二分。
  先写那一行「抽象成」，就会发现下标 i 绑定的三个值是不能分开动的。
- **475 pass1：从错的角度出发，一直补边界。** 先后以为问题出在 overlap、头尾，其实是 §2 的视角问题。
  补边界补了两轮还有新反例，就该停下来怀疑建模，而不是继续补。
- **475 pass1：下标和距离混着用。** `bisect` 返回的是数组下标，不是坐标上的距离，
  `distance.append(idx)` 和 `idx >= houses[-1]` 都是把两种量混在一起。
- **OA 第 1 题：没读懂 basetime 是干什么的。** 复盘时自己的结论是「好好 debug 好好读能过」。读题本身就是建模的一部分。
