class Solution:
    def findPeakElement(self, nums: list[int]) -> int:
        l=0
        r=len(nums)-2 # upperbound for r
        while l<=r:
            mid=(l+r)//2
            if nums[mid]<nums[mid+1]: # up
                l=mid+1  # mid=l-1
            elif nums[mid]>nums[mid+1]:
                r=mid-1 #  mid = r+1
            else:
                return mid
        # 迭代的条件保证
        #    l-1 ↗ l      ...      r+1 ↘ r+2
        # 退出loop是，我们是 r,l 临近，从而两个条件overlap在一起，从而l是peak
        return l
        