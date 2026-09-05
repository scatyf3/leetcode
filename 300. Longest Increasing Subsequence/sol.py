class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        n = len(nums)
        dp = [1] * n                       # 以 i 结尾, 至少是它自己 —— 边界条件就这一行
        for i in range(n):                 # 从 0 开始, i=0 时内层不转, 天然正确
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)                     # 不是 dp[-1]
