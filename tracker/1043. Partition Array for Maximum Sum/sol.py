class Solution:
    def maxSumAfterPartitioning(self, arr: list[int], k: int) -> int:
        n = len(arr)
        dp = [0] * (n + 1) # 前 i 个元素分割后能得到的最大总和
        for i in range(1, n + 1): # for each pos
            mx = 0
            for j in range(1, min(k, i) + 1):   # 最后一段长度 j
                mx = max(mx, arr[i - j])         # 段内最大值，边扩边更新
                dp[i] = max(dp[i], dp[i - j] + mx * j)
        return dp[n]