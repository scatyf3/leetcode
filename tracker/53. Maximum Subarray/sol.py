class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        '''
        how to iterate: l and r or dp slice
        但lr不保证任何异动顺序，只能写naive，但是这里边界收缩好算 O(n)
        dp slice? 但好像也一样，O(n)
        感觉好像这俩本质一样

        agent: 这里消复杂度的关键是1d dp，里面存以i为结尾的最大和
        '''
        n = len(nums)
        dp = []
        for i in range(n):
            dp.append(nums[i])
        for i in range(1,n):
            dp[i]=max(dp[i-1]+nums[i],nums[i]) # 连续or 切割
        return max(dp)
        