import heapq


class MedianFinder:
    '''
    对顶堆(two heaps)。addNum O(log n), findMedian O(1) —— sol.py 的 O(n) 插入的改进版。

    核心洞察: 求中位数不需要全局有序,只需要知道"中间那个/两个是谁"。
    排序给了远超需求的信息,代价是插入 O(n);
    对顶堆只维护"中间的分界线",所以能做到 O(log n)。
    (和 23. Merge k Sorted Lists 用堆的动机相同: 只关心极值时,别排序。)
    '''

    def __init__(self):
        self.lo = []   # 大顶堆(Python 没有,存负数模拟) —— 较小的一半
        self.hi = []   # 小顶堆                        —— 较大的一半

    def addNum(self, num: int) -> None:
        # 负数insert小heap，「最大的负数」=>「最小的正数」
        heapq.heappush(self.lo, -num)
        # 过一遍low heap，把里面的最大值搬到high
        # 这里假设两者均衡，low = {-1,-2}，high = {5} 此刻来了-7
        # 然后把-7丢到high，转换为真实值
        heapq.heappush(self.hi, -heapq.heappop(self.lo))   
        # 把 hi 的最小值搬回 lo
        if len(self.hi) > len(self.lo):                   
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]                # 奇数个,中位数就是 lo 的堆顶
        return (-self.lo[0] + self.hi[0]) / 2


# ============================================================
# 为什么那三行不用分类讨论也对
# ============================================================
#
# 正确性只靠两个不变量:
#   1) lo 里所有元素 <= hi 里所有元素
#   2) len(lo) == len(hi)  或  len(lo) == len(hi) + 1
#
# 第 1 步 push 到 lo 可能破坏不变量 1(num 可能很大),
# 第 2 步立刻把 lo 的最大值弹给 hi —— 这一步之后不变量 1 一定成立,
#         但可能把 hi 撑得比 lo 多一个,破坏不变量 2,
# 第 3 步把 hi 的最小值弹回 lo —— 只动最小值,不会破坏不变量 1。
#
# 三步走完两个不变量都恢复。有了它们,中位数永远在堆顶,O(1) 取。
#
#
# ---- Python 没有大顶堆 -----------------------------------------
# heapq 只有小顶堆。存 -num、取的时候再取负,就是大顶堆。
# 注意 findMedian 里 -self.lo[0] 那个负号别漏。
#
#
# ---- follow up ------------------------------------------------
# 1) 所有数都在 [0, 100]: 开个长度 101 的计数数组,addNum O(1),
#    findMedian 扫一遍前缀和找第 n//2 个 -> O(100) = O(1)。
# 2) 99% 在 [0, 100]: 计数数组管中间那 99%,两端各挂一个有序结构
#    记录离群值,再按总数定位中位数落在哪一段。
