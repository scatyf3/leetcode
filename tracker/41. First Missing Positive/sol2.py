class Solution:
    def firstMissingPositive(self, nums: list[int]) -> int:
        # for element, swap to index
        iterate_counter = 0
        write = 0
        n = len(nums)
        valid_pos = 0
        while iterate_counter<n:
            val = nums[write] # 把value swap到后面
            # print("current index and value",write,val)
            if 1<=val<=n: # index is [0,n-1] thus value is [1,n]
                # value start from 1 and pos start from 0
                nums[write],nums[val-1] = nums[val-1],nums[write]
                # print("swap",write,val-1)
            else:
                write+=1
                # print("write",write)
            iterate_counter+=1
        
        for idx in range(0,len(nums)):
            if nums[idx]!=idx+1:
                return idx+1
        return n+1