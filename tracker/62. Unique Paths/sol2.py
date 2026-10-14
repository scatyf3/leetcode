class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        # 解析解：C(m+n-2, m-1)
        N = m + n - 2          # 总步数
        k = min(m, n) - 1      # 挑较小的那边，循环次数更少
        res = 1
        for i in range(1, k + 1):
            res = res * (N - k + i) // i   # 先乘再整除
        return res
        # 或者直接 return math.comb(m + n - 2, m - 1)
