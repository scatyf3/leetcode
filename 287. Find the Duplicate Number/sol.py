class Solution:
    def findDuplicate(self, nums: List[int]) -> int:
        '''
        You must solve the problem without modifying the array nums and using only constant extra space.
        1 <= nums[i] <= n
        nums.length == n + 1
        '''
        nums.sort()
        i=0
        j=1
        n=len(nums)
        while j<n:
            if nums[i]==nums[j]:
                return nums[i]
            i+=1
            j+=1
        
        