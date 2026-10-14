
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        n = len(nums)
        dp = [False for i in range(n)]
        dp[0]=True
        for i in range(n):
            reach_dist = nums[i]
            if dp[i]: # 如果本身是reachable，再找别人 
                for j in range(i+1,min(i+1+reach_dist,n)):
                    dp[j]=True
        return dp[n-1]