from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        '''
        Input:
        - nums: List[int], 1 <= len(nums) <= 1e5, -1e4 <= nums[i] <= 1e4
        - k: int, 1 <= k <= 不同元素个数 m  (题目保证答案唯一)
        Target: 返回出现频次最高的 k 个元素
        Return: List[int], 顺序任意
        Output: List[int]

        解法: 桶排序 (bucket sort) O(n) 时间 / O(n) 空间   <- 面试写这版

        为什么能突破 O(m log m):
        堆和排序都是**比较**出来的, 比较排序的信息论下界就是 O(m log m)。
        想更快必须找一个不靠比较的性质 —— 这里的性质是:
            排序的 key 是"频次", 而频次一定落在 [1, n] 这个有界小整数区间里。
        key 是有界整数 -> 直接拿 key 当数组下标, 一次寻址代替 log 次比较。

        三步:
        1. Counter:  元素 -> 频次             O(n)
        2. 反向索引: 频次 -> [该频次的元素]    O(m), 长度 n+1 的数组, 下标即频次
        3. 从高频次往低走, 收够 k 个就停       O(n + m)

        为什么第 3 步是 O(n+m) 而不是 O(n*m):
        外层最多走 n+1 个下标, 内层遍历的元素总数恰好是所有桶之和 = m。
        两者是**相加**不是相乘 —— 内层每转一圈就永久消耗掉一个元素。
        '''
        n = len(nums)
        cnt = Counter(nums)                       # 1. 元素 -> 频次

        # 2. 反向索引: buckets[f] = 所有出现了 f 次的元素
        #    下标 0 空着不用 (频次最小是 1), 换来下标和频次直接对齐, 不用 -1
        buckets = [[] for _ in range(n + 1)]
        for key, freq in cnt.items():
            buckets[freq].append(key)

        # 3. 从最高频次 n 往下扫。空桶的内层循环转 0 次, 自然跳过, 不用特判
        res = []
        for freq in range(n, 0, -1):
            for key in buckets[freq]:
                res.append(key)
                if len(res) == k:                 # 一个桶里有 3 个但只差 2 个名额时,
                    return res                    # 必须在内层 return, 不能等桶走完
        return res                                # 理论上到不了 (k <= m 保证收得够)

        '''
        Dry Run: nums = [1,1,1,2,2,3], k = 2   n=6, cnt={1:3, 2:2, 3:1}
        建桶 (长度 7):
            buckets = [[], [3], [2], [1], [], [], []]
                       0    1    2    3   4   5   6      <- 下标 = 频次
                            ^    ^    ^
                            |    |    +-- 元素 1 出现 3 次
                            |    +------- 元素 2 出现 2 次
                            +------------ 元素 3 出现 1 次
        倒扫:
            freq=6,5,4  空桶, 内层不进
            freq=3      key=1 -> res=[1]     len=1 != 2, 继续
            freq=2      key=2 -> res=[1,2]   len=2 == k -> return
        return [1,2]

        Test Cases:
        [1,1,1,2,2,3], k=2  -> [1,2]   基本情形
        [1], k=1            -> [1]     n=1, buckets 长度 2
        [1,2], k=2          -> [1,2]   频次全相同, 都堆在 buckets[1],
                                       一个桶连收 2 个 -> 测的就是"内层 return"
        [4,4,4,4], k=1      -> [4]     m=1, 元素落在最高桶 buckets[4]
        [-1,-1,-2], k=1     -> [-1]    负数: 当下标的是**频次**不是元素值,
                                       元素只是桶里的内容, 负数完全无所谓
        [3,3,2,2,1], k=2    -> [3,2]   buckets[2]=[3,2], 一桶收满
        (另有 2000 组随机对拍 vs Counter.most_common, 全部一致)
        '''

    def topKFrequentLazy(self, nums: List[int], k: int) -> List[int]:
        '''
        工程版: 桶只开到 max(freq), 且用 None 占位 + 惰性建 list。

        上面那版渐进是 O(n), 但 Python 里实测反而可能比堆慢, 原因全在常数:
        `[[] for _ in range(n+1)]` 要真的 new 出 n+1 个 list 对象。
        n=300000 时就是 30 万次对象分配, 而真正用到的桶不超过 m 个。
        这是"渐进复杂度赢了、实际跑输"的典型 —— 分配开销不在 O() 里, 但它真实存在。

        两处改动:
        1. 桶只开到 hi = max(cnt.values())。随机数据下 hi 往往只有十几,
           数组瞬间从 30 万缩到 14。
        2. 但倾斜数据下 hi 可能逼近 n (比如一半元素都是同一个数, hi=150000),
           所以还要用 None 占位、真有元素时才建 list —— [None]*hi 是一次
           memset 级别的操作, 比建 hi 个 list 对象便宜一两个数量级。
        '''
        cnt = Counter(nums)
        hi = max(cnt.values())                    # 最高频次, 通常远小于 n

        buckets = [None] * (hi + 1)               # None 占位, 不预建 list
        for key, freq in cnt.items():
            if buckets[freq] is None:
                buckets[freq] = [key]
            else:
                buckets[freq].append(key)

        res = []
        for freq in range(hi, 0, -1):
            bucket = buckets[freq]
            if bucket is None:                    # 惰性版必须显式跳过空桶
                continue
            for key in bucket:
                res.append(key)
                if len(res) == k:
                    return res
        return res

        '''
        Benchmark: n=300000, 含 Counter 成本, 10 次均值

        随机数据 (m=94982, max_freq=13):
                             k=10      k=1000    k=50000
          sol.py  全推堆     42.0ms    41.6ms    87.1ms
          sol2    无守卫     48.8ms   154.3ms   100.6ms
          sol2    带守卫     25.7ms    27.0ms    52.8ms
          sol3    桶 (n+1)   72.8ms    74.1ms    77.8ms   <- 渐进最优却最慢
          sol3    桶 (惰性)  25.3ms    24.5ms       ~25ms <- 且与 k 无关

        倾斜数据 (m=47502, max_freq=150003, 一半元素是同一个数):
                             k=10      k=1000
          sol2    带守卫     17.4ms    18.9ms
          sol3    桶 (n+1)   64.7ms    64.5ms
          sol3    桶 预建    40.0ms    45.9ms   <- 只缩 size 不够, hi 本身就大
          sol3    桶 (惰性)  21.8ms    21.4ms   <- 两种分布下都稳

        结论:
        - 桶排序唯一"结构性"的优势是**与 k 完全无关**: k=10 和 k=50000 同样快,
          而堆版随 k 增大稳定变慢 (25.7 -> 52.8ms)。k 大时选桶。
        - 但 k 很小时它并不自动赢, 因为此时两者的瓶颈都已经是 Counter 那一遍 O(n)。
        - 什么时候不该用桶: 数据是流式的、n 事先不知道 -> 只能用大小 k 的堆 (空间 O(k))。
        '''
