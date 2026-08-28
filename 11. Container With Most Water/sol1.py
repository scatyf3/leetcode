class Solution:
    def maxArea(self, height: List[int]) -> int:
        # right max
        n = len(height)
        rightmax=[0 for i in range(n)]
        rightmax[n-1]=height[n-1]
        for i in range(n-2,-1,-1):
            rightmax[i] = max(height[i],rightmax[i+1]) # curr vs prev rightmax
        # greedy search for max water
        max_water = -1
        for i in range(n):
            j=i+1
            while j < n:
                max_water = max(min(height[i],rightmax[j]) * (j-i),max_water)
                j += 1
        return max_water

        '''
        我的第一版(naive)。O(n^2) 时间 / O(n) 空间。
        对拍结论: 答案正确(5000 组随机 vs 暴力, 零反例), 但 rightmax 是多余的。

        为什么带着 rightmax 也不会错:
          rightmax[j] 在某个 k >= j 处取到, 所以
            算出来的 min(h[i], rightmax[j]) * (j-i)
              <= min(h[i], h[k])          * (k-i)     <- 一个真实存在的容器
          即每个候选值都不高估; 而 j 扫到 k 那一轮又恰好取到等号。
          "不高估 + 能取到" => 最大值正确。

        但它一点好处都没有: 复杂度还是 O(n^2), 白多了 O(n) 空间。
        把 rightmax[j] 换成 height[j] 就是纯暴力, 完全等价。

        病根: rightmax/leftmax 是 LC42 接雨水的模板, 搬错题了。
          LC42: 位置 i 头顶的水 = min(左最大, 右最大) - h[i]  -> 依赖"看不见的远处", 必须预处理
          LC11: 容器只由两根墙决定 = min(h[l], h[r]) * (r-l)  -> 两根墙就在手上, 中间柱子不挡水
        迁移模板前先问: 这题的答案依赖我手上没有的信息吗? 不依赖就不需要预处理数组。

        踩过的坑(第一版):
          1. while j < n 里漏了 j += 1   -> 死循环
          2. max_water = ... 直接覆盖    -> 没累加, 只留最后一次的值
          3. max_water = -1 初值: 题目保证 n >= 2, 侥幸没事; 写 0 更稳

        下一步: 双指针 O(n) / O(1), 见 sol2.py(还没写)。
        '''
