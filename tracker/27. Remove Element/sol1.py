class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        '''
        var:
        - nums: List[int]
        - val: int
        Change nums:
        k element is not eq to val
        valid slice: nums[0:k] slices means the non equal zone
        How: swap tail and valid slice
        Return: 
        - the number of elements in nums which are not equal to val
        '''
        no_eq_count=0
        tail_index=len(nums)-1 # not valid slice[tail_index:len(nums)-1]
        i=0
        while(i<=tail_index):
            if(nums[i]==val):
                # swap
                # after sweeping, current nums[i] is not scaned, thus we need a better indexing to iterate throught nums
                tmp=nums[i]
                nums[i]=nums[tail_index]
                nums[tail_index]=tmp
                tail_index-=1
            else:
                no_eq_count+=1
                i+=1
        return no_eq_count
    
'''
Error:
1. 
'''
