class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        if len(nums)==0:
            return [-1,-1]
        # left bound
        l=0
        r=len(nums)-1
        mid=(l+r)//2
        left_bound=-1
        while (l<=r):
            if nums[mid]<target:
                l=mid+1
            else:
                r=mid-1
            mid=(l+r)//2
        left_bound=l
        if l>=len(nums) or nums[l]!=target: # target not in nums
            return [-1,-1]
        # right bound
        l=0
        r=len(nums)-1
        mid=(l+r)//2
        right_bound=-1
        while (l<=r):
            if nums[mid]<=target:
                l=mid+1
            else:
                r=mid-1
            mid=(l+r)//2
        right_bound=r # 这里是左缝
        return [left_bound,right_bound]
