---
title: 堆的用法
status: draft
order: 15
alias: []
related: [/structures/heap, /python/heapq, /structures/ordered-set]
---

# 堆的用法

堆只回答一个问题：**当前这堆东西里最小的是谁**，而且插一个、弹一个都只要 O(log n)。
所以用堆的题，区别不在怎么调 API（见 [heapq](../python/heapq.md)），而在**堆里放的是什么**、**堆有多大**。
结构本身、常驻还是随用随建，见 [堆](../structures/heap.md)。

| 堆里放的是 | 子类 | 堆多大 | 题 |
|---|---|---|---|
| 目前为止的前 k 名 | §1 大小为 k 的堆 | k | 215、703、347、973 |
| 每一路当前的头 | §2 k 路归并 | 路数 k | 23、355 |
| 较小的一半 / 较大的一半 | §3 对顶堆 | 各 n/2 | 295 |
| 所有还能选的候选 | §4 贪心：每次拿最大的 | n | 1046、1405、621 |

> 拿到题先问：**堆里每一格代表什么？** 答出来，什么时候 push、什么时候 pop 就定了。

## 1. 大小为 k 的堆：前 k 大用**小**根堆

要前 k 大，堆里只留 k 个。堆顶是这 k 个里最小的那个，正好是**进门的门槛**：

```
k = 3，目前的前 3 大 {5, 8, 9}，小根堆，堆顶 5 = 门槛
来了 7：7 > 5 → 5 出局，7 进来   → {7, 8, 9}，门槛变成 7
来了 3：3 < 7 → 进不来，堆不动
```

被踢出去的那个已经被 k 个数压在下面，后面只会来更多竞争者，它不可能再回到前 k。堆永远只有 k 个，总共 O(n log k)。

```python
def findKthLargest(self, nums: List[int], k: int) -> int:     # LC 215
    h = nums[:k]
    heapq.heapify(h)
    for elem in nums[k:]:
        if elem > h[0]:              # 守卫：比门槛小的连堆都不进
            heapq.heappop(h)
            heapq.heappush(h, elem)
    return h[0]
```

- **堆还没满 k 个时无条件 push**，不能先和堆顶比（703：`k=3, nums=[4,5]`，`add(3)` 要返回 3）。
- **守卫那一行不能省**。347 的 [sol2](https://github.com/scatyf3/leetcode/blob/main/tracker/347.%20Top%20K%20Frequent%20Elements/sol2.py)
  先写成「每个都 push，超过 k 就 pop」，k 小时实测比全推进堆**还慢**（`heappush` 一两层就停，`heappop` 每次沉到底）；
  加上 `if freq > hp[0][0]` 快了 3 倍。`heapq.nlargest` 内部也是这么做的。
- 前 k **小**（973 最近的 k 个点）方向反过来，用大根堆存 `-dist`。我 973 是全部推进小根堆再弹 k 次，O(n log n)，也能过。
- **key 有界就别用堆**：347 的频次落在 `[1, n]`，开桶 `buckets[freq]` 就是 O(n)
  （[347 的 note](https://github.com/scatyf3/leetcode/blob/main/tracker/347.%20Top%20K%20Frequent%20Elements/note.md)）。
  堆稳赚的是空间 O(k) 和数据流（703，n 事先不知道）。

## 2. k 路归并：每一路只占一个坑

k 条各自有序的链，合起来的最小值一定是某一条的**头**。所以堆里只放 k 个头，弹一个，就把它那一路的下一个补进来：

```python
def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:   # LC 23
    res = ListNode()
    tail = res
    h = []
    for k, head in enumerate(lists):     # k = 第几个链表
        if head:                         # 空链表要跳过
            heapq.heappush(h, (head.val, k, head))
    while len(h) != 0:
        val, k, node = heapq.heappop(h)
        if node.next is not None:
            heapq.heappush(h, (node.next.val, k, node.next))
        tail.next = node
        tail = tail.next
    return res.next
```

堆里任何时刻最多 k 个，所以是 O(N log k) 而不是 O(N log N)。中间那个 `k` 是打平局用的，原因见 [heapq](../python/heapq.md)「元组比较打平」。

- **补货时键和值要对上**（23 踩过）：写成 `heappush(h, (node.next.val, k, node))`，键取了下一个节点的值，塞的却是当前节点。
  同一个节点被弹两次，接成自环，最后崩在下游的 `AttributeError`。报错在下游，病根在上游。

355 的 `getNewsFeed` 是同一道题换了皮：每个关注的人的推文按时间 append，本来就有序，
每人把**最新一条**入堆，弹一条就补那个人的前一条，弹够 10 条停。
我第一版是把所有人的所有推文都推进堆再弹 10 次，也能 AC，只是慢。

## 3. 对顶堆：只维护中间那一刀

中位数不需要全局有序，只需要知道中间那一两个是谁。把数据切成两半，各用一个堆盯住靠中间的那头：

```
     lo：大根堆（存负数）         hi：小根堆
       较小的一半                  较大的一半
     [1  2  3]  堆顶 3    |    堆顶 4  [4  5]
                      中位数就在这两个堆顶上
```

两个不变量：`lo` 里每个数 ≤ `hi` 里每个数；`len(lo)` 等于 `len(hi)` 或多一个。

```python
class MedianFinder:                          # LC 295
    def __init__(self):
        self.lo = []   # 大顶堆（存负数）—— 较小的一半
        self.hi = []   # 小顶堆          —— 较大的一半

    def addNum(self, num: int) -> None:
        heapq.heappush(self.lo, -num)                       # 先推进 lo
        heapq.heappush(self.hi, -heapq.heappop(self.lo))    # lo 的最大值搬给 hi：不变量 1 恢复
        if len(self.hi) > len(self.lo):                     # hi 多了就把最小值搬回 lo：不变量 2 恢复
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]               # 负号别漏
        return (-self.lo[0] + self.hi[0]) / 2
```

三行不用分类讨论。我最早写的是有序数组 + 二分插入（[sol.py](https://github.com/scatyf3/leetcode/blob/main/tracker/295.%20Find%20Median%20from%20Data%20Stream/sol.py)），
以为也是 O(log n)。不是：二分找位置 O(log n)，`list.insert` 挪元素 O(n)，瓶颈在修复不在查找 ——
有序数组维护「两两有序」，比题目要的强太多。这条线（要多少有序就付多少钱）见
[128 的 note](https://github.com/scatyf3/leetcode/blob/main/tracker/128.%20Longest%20Consecutive%20Sequence/note.md) 末尾。

## 4. 贪心：每次拿剩得最多的

1046 是最纯的版本：取负当大根堆，每轮弹两个最重的，差值压回去。坑只有一个：两个都是负数，
压回去的差值要保持负号，`stone_1 - stone_2`（先弹出的更重）。

麻烦一点的是「拿最多的，但不能连着拿同一个」。1405 每轮把三种字母按剩余数 `cnt.sort(reverse=True)`，
先试最多的，放了会三连（`res[-2:] == [ch, ch]`）就退而放第二多的，两个都放不了就结束
（[sol.py](https://github.com/scatyf3/leetcode/blob/main/tracker/1405.%20Longest%20Happy%20String/sol.py)）。
只有三种，排序就够了；种类多的时候换成堆，「第一不行试第二」就是弹两次。
621 的约束换成了冷却 n 格：暂时不能拿的**移出堆、进一个 deque 等冷却**，到点再推回堆
（[sol2.py](https://github.com/scatyf3/leetcode/blob/main/tracker/621.%20Task%20Scheduler/sol2.py)）。
它有 O(n) 的公式解，推不出公式时这个模拟是省脑子的那条路。
