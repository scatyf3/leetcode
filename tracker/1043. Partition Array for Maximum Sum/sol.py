class Solution:
    def maxSumAfterPartitioning(self, arr: list[int], k: int) -> int:
        n = len(arr)
        dp = [0] * n  # dp[i]：arr[0..i] 分割后的最大和

        for i in range(n):
            mx = 0
            for j in range(1, min(k, i + 1) + 1):   # 最后一段长度 j
                mx = max(mx, arr[i - j + 1])        # 这一段最左边的元素
                prev = dp[i - j] if i - j >= 0 else 0
                dp[i] = max(dp[i], prev + mx * j)

        return dp[-1]
