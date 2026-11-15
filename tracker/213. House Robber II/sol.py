class Solution:
    def rob(self, nums: list[int]) -> int:
        # naive: 2d dp, iterate start first
        # advanced: pass1, find max as start, then dp
        if len(nums)==1:
            return nums[0]
        if len(nums)==2:
            return max(nums[0],nums[1])

        # pass 1
        dp = [0 for i in range(len(nums))] # best sum in curr index
        dp[0]=nums[0]
        dp[1]=nums[0]
        for i in range(2,len(nums)-1): # 
            dp[i]=max(dp[i-1],dp[i-2]+nums[i])
        max_pass1 = dp[len(nums)-2] # dp[len(nums)-1] must eq prev, cause we do not select that
        # pass 2
        dp = [0 for i in range(len(nums))] # best sum in curr index
        dp[0]=0
        dp[1]=nums[1]
        for i in range(2,len(nums)):
            dp[i]=max(dp[i-1],dp[i-2]+nums[i])
        max_pass2 = dp[len(nums)-1]
        return max(max_pass1,max_pass2)