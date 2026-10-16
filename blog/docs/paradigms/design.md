---
title: 设计题
status: draft
order: 19
alias: []
related: [/structures/hash-table, /structures/linked-list, /structures/heap, /paradigms/stack, /structures/trie]
---

# 设计题

设计题给你一组 API，外加每个操作要达到的复杂度，要做的是**挑数据结构，让每个操作都踩中那个复杂度**。
它不是 system design，也几乎不需要新算法：最难的那个操作，通常就是一道做过的经典题换了皮。
所以难点只有两处：选对结构的组合，以及把几份结构**同步**维护对 —— 146 前后写了四遍，pass 2 的三个坑全是「只改了一边」。

## 怎么想：先列 API，再挑结构

355 的 note 里定下的三步：

1. 列出每个 API，写清它**读**哪些状态、**写**哪些状态
2. 每份状态挑一个结构：要按 key 查用 `dict`，要去重用 `set`，按时间追加用 `list`
3. 找出最难的那个操作，它通常就是一道经典题

| 题 | 状态 → 结构 | 最难的操作 | 其实是 |
|---|---|---|---|
| 146 LRU | `key → 节点`；使用顺序 → 双链表 | 满了淘汰最久没用的 | 双链表 O(1) 摘下 / 插头 |
| 155 Min Stack | 主栈 + 每层的最小值 | `getMin` | 辅助栈（[stack.md](stack.md) §5） |
| 208 Trie | 一个字符一条边的树 | `startsWith` | [trie.md](../structures/trie.md) |
| 295 中位数 | 小的一半 / 大的一半 | `findMedian` | 对顶堆 |
| 355 Twitter | `userId → [(time, tweetId)]`；`userId → set` | `getNewsFeed` | 合并 k 个有序列表（23） |
| 432 All O\`one | `key → 次数`；`次数 → keys` | O(1) 拿最大 / 最小次数 | 桶串成双链表 |
| 703 第 k 大 | 大小为 k 的最小堆 | `add` 后返回第 k 大 | top-k（215） |
| 981 TimeMap | `key → 平行数组 times / vals` | `get(key, t)` | 二分搜缝「最后一个 ≤ t」 |

355 的 bug 全出在杂活上：tweetId 不代表时间，要自己维护全局自增的 `time`；自己的推文也要算进 feed；
`unfollow` 用 `set.discard`（没关注过也不报错）；`dict` 换成 `defaultdict` 能省掉一堆 `if key not in`。

## 哈希表 + 一个顺序结构

哈希表给 O(1) 定位，但不记顺序（[hash-table.md](../structures/hash-table.md) §6）。
设计题最常见的组合就是在它旁边再挂一个顺序结构：**题目要的是哪种顺序，就挂哪种结构**。

| 要的顺序 | 挂什么 | 题 |
|---|---|---|
| 最近使用时间，要 O(1) 挪到最前、删掉最后 | 双链表 | 146 |
| 次数，每次只 ±1 | 按次数排的桶，串成双链表 | 432 |
| 时间戳，只会追加 | `list`（append 即有序）+ 二分 | 981、355 |

146 的完整代码和「摘下 2 根、插入 4 根」见 [linked-list.md](../structures/linked-list.md) §「双向链表」，这里不重复。

**432 是同一个骨架，节点从「一个 key」换成「一桶 key」。** 第一版想的是两张哈希表，卡在 O(1) 拿最大 / 最小：
次数一直在变，堆的 inc / dec 要 O(log n)。能做到 O(1) 靠题面里没用上的那条：**次数一次只变 1**，
所以 key 只会挪到**相邻**的桶。

```python
class Bucket:
    def __init__(self, cnt):
        self.cnt = cnt
        self.keys = set()               # 次数都是 cnt 的 key，set 增删 O(1)
        self.prev = self.next = None


class AllOne:

    def __init__(self):
        self.head = Bucket(0)           # 哨兵：head.next 次数最小，tail.prev 次数最大
        self.tail = Bucket(float('inf'))
        self.head.next, self.tail.prev = self.tail, self.head
        self.where = {}                 # key -> 它所在的 Bucket

    # ---- 两个原语：桶的插入 / 删除，指针只在这里写 ----
    def _insert_after(self, node, cnt):
        b = Bucket(cnt)
        b.prev, b.next = node, node.next
        node.next.prev = b
        node.next = b
        return b

    def _remove(self, b):
        b.prev.next = b.next
        b.next.prev = b.prev

    def inc(self, key: str) -> None:
        cur = self.where.get(key, self.head)        # 新 key 当作在次数 0 的 head 里
        nxt = cur.next
        if nxt.cnt != cur.cnt + 1:                  # 次数 +1 的桶还不存在 → 紧挨着 cur 新建
            nxt = self._insert_after(cur, cur.cnt + 1)
        nxt.keys.add(key)
        self.where[key] = nxt
        if cur is not self.head:                    # 先放进新桶，再从旧桶删
            cur.keys.discard(key)
            if not cur.keys:
                self._remove(cur)
```

`dec` 是镜像，`getMaxKey` 读 `tail.prev`、`getMinKey` 读 `head.next`，完整版见
[sol_dll.py](https://github.com/scatyf3/leetcode/blob/main/tracker/432.%20All%20O%60one%20Data%20Structure/sol_dll.py)。
[432 的 note](https://github.com/scatyf3/leetcode/blob/main/tracker/432.%20All%20O%60one%20Data%20Structure/note.md) 里还对比了一版更短的「两张哈希表 + `mn` / `mx` 两个变量」：只有一处不是 O(1) ——
把最后一个次数为 1 的 key 减没了，得往上扫找新的最小次数。**链表在这里提供的就是一件事：「下一个非空的次数」不用找，`cur.next` 直接给。**

146 和 432 收敛到同一个写法：**两份结构只在两三个 helper 里改，每个 helper 同时改两边**，主逻辑只调 helper
（146 pass 4 的三点见 [linked-list.md](../structures/linked-list.md)）；写完和暴力解随机对拍（432 两版各拍了 3000 组操作序列）。

981 最简单：timestamp 保证递增，`key → [times], [vals]` 直接 append 就有序，不用 `{key: {t: v}}`。
`get` 二分搜缝 `times[mid] <= t`，返回 `vals[r]`（`r < 0` 返回 `""`）；不用单独判 `==` 命中（[binary-search.md](binary-search.md)）。

## 堆：只要最值，不要全序

- **295**：最朴素的是维护一个有序数组，二分找位置 O(log n)，但插入要挪元素，O(n)。
  中位数只要求「中间那一刀」是精确的，两边各自不必有序 → 大顶堆装小的一半、小顶堆装大的一半，修复只要 O(log n)。
  295 的 note 把它归成一条跨题的规律：**维护不变式的代价 ∝ 不变式的强度**
- **703**：大小为 k 的最小堆，堆顶就是第 k 大。坑：堆还不满 k 个时要无条件 push，不能先和堆顶比（`k=3, nums=[4,5], add(3)` 应返回 3）
- **355**：feed 的候选随 userId 和当前关注关系变，所以不常驻，每次 `getNewsFeed` 临时建堆。
  自己的第一反应是维护一个全局的堆、发推时就推送 —— 那是推 / 拉两种方案的取舍，口头讲清楚即可，代码先写简单正确的那个。
  什么时候常驻、什么时候随用随建，见 [heap.md](../structures/heap.md)

堆不支持删除任意元素。要删就两条路：像 355 那样随用随建，或者懒删除 —— 先记下「它已经作废」，等它浮到堆顶被弹出时再扔掉
（[python/heapq.md](../python/heapq.md)）。仓库里还没有用到懒删除的题。

## 练手：手写一遍数据结构

设计题之外，LeetCode 上还有一批题就是「把某个结构自己写一遍」：

| 题 | 写什么 | 仓库 |
|---|---|---|
| 705 / 706 Design HashSet / HashMap | 拉链法；答案就是 [hash-table.md](../structures/hash-table.md) §0 那 20 行 | — |
| 707 Design Linked List | dummy + 删前驱 + 按下标走 | [建了，未写](https://github.com/scatyf3/leetcode/blob/main/tracker/707.%20Design%20Linked%20List/note.md) |
| 146 LRU Cache | 哈希表 + 双链表 | [✓](https://github.com/scatyf3/leetcode/blob/main/tracker/146.%20LRU%20Cache/note.md) |
| 460 LFU Cache | 146 + 432 合体：每个次数桶里一条 LRU 链 | — |
| 432 All O\`one | 桶双链表 | [✓](https://github.com/scatyf3/leetcode/blob/main/tracker/432.%20All%20O%60one%20Data%20Structure/note.md)（两版都写了，status 还是 todo） |
| 155 Min Stack | 辅助栈 | [✓](https://github.com/scatyf3/leetcode/blob/main/tracker/155.%20Min%20Stack/note.md) |
| 232 / 225 | 两个栈拼队列 / 队列拼栈 | — |
| 622 / 641 | 循环队列 / 循环双端队列：定长数组 + 头下标 + size，下标取模 | — |
| 912 Sort an Array | 手写堆排序（下沉） | — |
| 215 Kth Largest | 不用 heapq：快速选择，或手写堆 | [用 heapq 做过](https://github.com/scatyf3/leetcode/blob/main/tracker/215.%20Kth%20Largest%20Element%20in%20an%20Array/note.md) |
| 208 Implement Trie | 字典树 | [✓](https://github.com/scatyf3/leetcode/blob/main/tracker/208.%20Implement%20Trie%20%28Prefix%20Tree%29/note.md) |
| 211 / 212 | Trie + `.` 通配时 DFS / Trie + 网格回溯 | — |
| 380 Insert Delete GetRandom O(1) | `dict` 值→下标 + `list`；删除时和末尾交换再 pop | — |
| 547 / 684 | 并查集（路径压缩） | — |
| 307 Range Sum Query - Mutable | 树状数组 / 线段树 | — |
| 1206 Design Skiplist | 跳表 | — |
