class Solution:
    def maxValue(self, n: int, index: int, maxSum: int) -> int:
        def side(v, length):
            if length <= v - 1:
                return (v - 1 + v - length) * length // 2
            return v * (v - 1) // 2 + (length - (v - 1))

        l, r = 1, maxSum
        while l <= r:
            mid = (l + r) // 2
            total = side(mid, index) + mid + side(mid, n - index - 1)
            if total <= maxSum:   # T：这个峰值放得下
                l = mid + 1
            else:                 # F
                r = mid - 1
        return r                  # 最后一个 T
