import heapq


class MedianFinder:
    '''
    对顶堆的"直觉版": 先分类(num 该进哪个堆), 再平衡(长度差超了就搬一个)。
    和 sol2.py 完全等价, addNum O(log n), findMedian O(1)。

    不变量和 sol2.py 一样:
      (1) max(lo) <= min(hi)
      (2) len(lo) == len(hi)  或  len(lo) == len(hi) + 1
    区别只在于恢复不变量的手法: sol2 是"无脑破坏再修复", 这版是"小心翼翼不破坏"。
    '''

    def __init__(self):
        self.lo = []   # 大顶堆(存负数模拟) —— 较小的一半
        self.hi = []   # 小顶堆            —— 较大的一半

    def addNum(self, num: int) -> None:
        # ---- 第一步: 分类, 直接放进它该在的那半, 不破坏不变量 (1) ----
        # ★ not self.lo 这个短路必须有: 空堆时 self.lo[0] 会 IndexError。
        #   lo 空 => hi 也一定空(不变量 2 保证 lo 不会比 hi 短), 所以放哪边都行。
        if not self.lo or num <= -self.lo[0]: # 一个guard防止越界，否则访问[0]会炸
            heapq.heappush(self.lo, -num)
        else:
            heapq.heappush(self.hi, num)

        # ---- 第二步: 再平衡, 只可能坏一边, 且最多搬一个 ----
        if len(self.lo) > len(self.hi) + 1:      # lo 多了两个
            heapq.heappush(self.hi, -heapq.heappop(self.lo))
        elif len(self.hi) > len(self.lo):        # hi 多了一个
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2


# ============================================================
# 这版 vs sol2.py: 两种恢复不变量的风格
# ============================================================
#
# sol2 (无脑三步):   先故意破坏, 再用"搬极值"的操作强行修回来。
#                    没有分支, 但每次固定 3 次 push/pop, 常数大。
# sol3 (分类+平衡):  先判断, 尽量不破坏; 破坏了再修。
#                    多一个比较, 但大多数情况下只有 1 次 push, 常数小。
#
#
# ---- 为什么"最多搬一个"就够 ----------------------------------
# 进入 addNum 时 d = len(lo) - len(hi) ∈ {0, 1}(不变量 2)。
# 一次 push 只让某一边 +1, 所以 push 后 d ∈ {-1, 0, 1, 2}。
#   d = 2  -> lo 搬一个给 hi -> d = 0   ✓
#   d = -1 -> hi 搬一个给 lo -> d = 1   ✓
#   d ∈ {0,1} 本来就合法, 不动。
# 差值最多偏 1, 所以永远不需要循环搬, 一个 if/elif 就封死了。
# 两个分支互斥(d 不可能同时是 2 和 -1), 所以是 elif 不是两个 if。
#
#
# ---- 三个容易写错的地方 --------------------------------------
# 1. 忘了 not self.lo 短路 -> 第一次 addNum 就 IndexError。
# 2. 阈值写错: 是 len(lo) > len(hi) + 1, 不是 len(lo) > len(hi)。
#    写成后者会让 lo 永远不许比 hi 多, 和 findMedian 的奇数分支对不上。
# 3. num <= -self.lo[0] 里的负号。lo 存的是负数, 堆顶 self.lo[0] 是
#    "最大值的相反数", 要取负才能和 num 比。
#
# 相等时进 lo 还是 hi 都行 —— 相等元素不会破坏 max(lo) <= min(hi)。
#
#
# ---- 那么该写哪版 --------------------------------------------
# 面试里 sol2 更稳: 三行没有分支, 背下来不会错, 也不用讨论空堆。
# 要讲清楚思路时 sol3 更好: 它的每一步都对应"我在想什么"。
# 两版渐进复杂度相同, 都是 addNum O(log n) / findMedian O(1)。
