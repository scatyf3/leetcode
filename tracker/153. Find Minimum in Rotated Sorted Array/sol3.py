class Solution:
    def findMin(self, nums: List[int]) -> int:
        '''
        [3,4,5,1,2]
        mid>nums[l] and mid>nums[r] => in left-larger part, move right
        mid<nums[l] and mid<nums[r] => in right-smaller part, move left
        '''
        # binary search ver
        l=0
        r=len(nums)-1
        mid=int((l+r)/2)
        while l<=r:
            if nums[mid] > nums[-1]:      # was: nums[mid]>nums[l] and nums[mid]>nums[r]
                l=mid+1
            else:
                r=mid-1
            mid=int((l+r)/2)
        return nums[l]
        '''
        while l<=r:
            if nums[mid]>nums[l] and nums[mid]>nums[r]:
                l=mid+1
            else:
                r=mid-1
            mid=int((l+r)/2)
        return nums[l] # not mid?
        '''
        