class Solution:
    def findMin(self, nums: List[int]) -> int:
        '''
        O(logn), return min elem
        2 increasing part
        varient of binary search
        [increase1|increase2]
        or 
        [increase]
        case 1 l_start<r_end
        1 2 3 4 5
        case 2 l_start>r_end
        2 3 4 5 1
        3 4 5 1 2
        '''
        n = len(nums)
        if n==1:
            return nums[0]
        if (nums[0]<nums[n-1]): #  case 1
            return nums[0]
        else: # O(n)
            prev = nums[n-2]
            prev_idx = n-2
            curr = nums[n-1]
            curr_idx=n-1
            while(curr>prev and prev_idx>0):
                prev_idx-=1
                curr_idx-=1
                prev = nums[prev_idx]
                curr = nums[curr_idx]
            return nums[curr_idx]
