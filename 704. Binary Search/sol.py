class Solution:
    def search(self, nums: List[int], target: int) -> int:
        n = len(nums)
        l = 0
        r = n-1
        mid=(l+r)//2
        # edge case: r=l+1, here, mid const=l
        while(l<=r):
            if nums[mid]<target:
                l=mid+1 # skip self
            elif nums[mid]>target:
                r=mid-1 # skip self
            else:
                return mid
            mid=(l+r)//2
        return -1
        