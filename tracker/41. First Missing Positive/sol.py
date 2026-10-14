class Solution:
    def firstMissingPositive(self, nums: list[int]) -> int:
        n = len(nums)
        # 第一遍：把每个数 v 换到它该住的下标上
        for i in range(n):
            while 0 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                j = nums[i]-1
                nums[i], nums[j] = nums[j], nums[i]
        # 第二遍：找第一个住错人的位置
        for i in range(n):
            if nums[i] != i+1:
                return i+1
        return n+1
