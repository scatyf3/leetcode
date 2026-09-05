import heapq
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

        解法: 大小固定为 k 的**最小堆**  O(n + m log k) 最坏时间 / O(n + k) 空间
        和 sol.py 的区别: sol.py 把全部 m 个元素推进堆再弹 k 次, 最坏 O(m log m);
        这里堆里永远只留 k 个, 每次堆操作是 log k 而不是 log m。

        !! 但这个版本实测比 sol.py 更慢 (见文末 Benchmark), 因为 push/pop 代价不对称:
           heappush 期望 O(1)  (新元素向上冒, 遇到更小的父节点就停, 随机数据下一两层就停)
           heappop  恒定 Θ(log k) (末尾叶子搬到根, 必须一路下沉到底, 没有提前退出)
           -> 本版把 m 次便宜的 push, 换成了 m 次 push + m 次昂贵的 pop。
           O(m log k) 是**最坏情况**保证; 随机输入下 sol.py 的平均其实是 O(m)。
           要真的更快, 必须加守卫 -> 见下面的 topKFrequentGuarded。

        为什么可以直接扔掉堆顶: 堆里现在有 k+1 个元素, 堆顶是这 k+1 个里频次最小的。
        它已经被 k 个元素压在下面了, 后面只会进来更多竞争者, 排名只降不升
        -> 它永远进不了前 k, 现在扔和最后扔是一样的。

        注意: 不取负号。sol.py 用 -cnt 把最小堆当最大堆使 (要弹最大的);
        这里要弹掉的是**最小**的, 正好是最小堆的原生行为, 所以存正的频次。
        '''
        cnt = Counter(nums)                  # C 实现的计数, 比手写 for 循环快

        hp = []                              # 最小堆, 存 (freq, elem), 长度 <= k
        for key, freq in cnt.items():
            heapq.heappush(hp, (freq, key))
            if len(hp) > k:
                heapq.heappop(hp)            # 扔掉当前 k+1 个里频次最小的
            # python 只有最小堆

        # 堆里剩下的就是答案。弹出顺序是频次从小到大, 题目不要求顺序所以无所谓
        return [heapq.heappop(hp)[1] for _ in range(k)]

        '''
        Dry Run: nums = [1,1,1,2,2,3], k = 2   (cnt = {1:3, 2:2, 3:1})
        遍历 cnt.items() (Python 3.7+ 按插入序: 1, 2, 3)
            key=1 freq=3  push -> hp=[(3,1)]              len=1, 不超
            key=2 freq=2  push -> hp=[(2,2),(3,1)]        len=2, 不超
            key=3 freq=1  push -> hp=[(1,3),(3,1),(2,2)]  len=3 > 2
                          pop  -> 弹出 (1,3), hp=[(2,2),(3,1)]   <- 频次 1 的 3 被淘汰
        收尾: 弹 (2,2) -> res=[2]; 弹 (3,1) -> res=[2,1]
        return [2,1]   (期望 [1,2], 顺序任意 -> 通过)

        Test Cases:
        [1,1,1,2,2,3], k=2  -> [1,2]      基本情形
        [1], k=1            -> [1]        单元素
        [1,2], k=2          -> [1,2]      k == m, 堆从不触发 pop, 退化成 sol.py
        [4,4,4,4], k=1      -> [4]        全同元素, m=1
        [-1,-1,-2], k=1     -> [-1]       负数
        [3,3,2,2,1], k=2    -> [3,2]      1 只出现一次, 是唯一被淘汰的

        Benchmark: n=300000, m≈95000, 随机数据, Counter 成本已剥离, 取 10 次均值
                                  k=10      k=1000    k=50000
          sol.py  全推进堆        17.9 ms   18.1 ms    57.9 ms
          本版    留 k, 无守卫    27.1 ms   60.6 ms    55.8 ms   <- 反而更慢
          Guarded 留 k, 带守卫     5.2 ms    7.5 ms    28.7 ms   <- 快 3 倍
        对抗输入 (按频次递增序喂入, 触发 sol.py 的 O(m log m) 最坏情况), k=10:
          sol.py 23.7 ms  /  Guarded 5.3 ms   <- 这时 sol.py 才真的退化

        结论: 大小 k 的堆稳赚的是**空间** O(k) 和**最坏情况**保证;
              想同时赢时间必须加守卫。渐进复杂度在这里骗了人 ——
              O(m log m) 是 sol.py 的最坏而非平均, heappush 期望才 O(1)。

        还没写:
        - 频次有界在 [1, n] -> 桶排序 O(n), 见 sol3.py
        '''
    def topKFrequentGuarded(self, nums: List[int], k: int) -> List[int]:
        '''
        同样是大小 k 的最小堆, 只多了一行守卫: 堆满之后先跟堆顶比一次。
        比不过堆顶的元素连堆都不进 -> 一次比较, 零次堆操作。

        m 个随机元素里真正能挤进 top-k 的期望只有 O(k log(m/k)) 个,
        所以绝大多数迭代退化成"一次整数比较", 总体 ~O(n + m)。
        heapq.nlargest(k, cnt.keys(), key=cnt.get) 内部就是这个策略。
        '''
        cnt = Counter(nums)

        hp = []
        for key, freq in cnt.items():
            if len(hp) < k:
                heapq.heappush(hp, (freq, key))
            elif freq > hp[0][0]:                    # <- 守卫: 挤不进去就别动堆
                heapq.heappushpop(hp, (freq, key))   # push+pop 合成一次 sift
        return [key for _, key in hp]

