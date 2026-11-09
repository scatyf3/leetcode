class Solution:
    def maxValue(self, n: int, index: int, maxSum: int) -> int:

        def side(v, k):
            # 这一侧：从 v-1 开始往下减，最小到 1，共 k 个格子
            if k <= v - 1:
                # 情况 1：一段完整的等差数列
                first = v-1          # 紧挨峰值的那个数
                last  = v-k          # 第 k 个数
                return (first + last) * k // 2    # 先乘后除

            # 情况 2：v-1, ..., 1 之后全是 1
            arith = (v - 1) * v // 2             # 1 + 2 + ... + (v-1)
            ones  = k-v+1              # 还剩几个格子
            return arith + ones

        def total(v):
            left_k  = index
            right_k = n - 1 - index
            return v + side(v, left_k) + side(v, right_k)

        l, r = 1, maxSum
        while l <= r:
            mid = (l + r) // 2
            if total(mid) <= maxSum:
                l = mid + 1
            else:
                r = mid - 1
        return r

