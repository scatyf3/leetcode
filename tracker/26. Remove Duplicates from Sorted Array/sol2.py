class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        valid_prefix = 0
        for i in range(1, len(nums)):
            # if cur iterated element is not in valid prefix
            if nums[i] != nums[valid_prefix]:
                # add it to valid prefix
                valid_prefix+=1
                nums[valid_prefix] = nums[i]  
        return valid_prefix+1 # we should return next index of valid prefix
    
'''
indexing issue again
'''
