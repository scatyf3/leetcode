class Solution:
    def sortColors(self, nums: list[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        the same color are adjacent, with the colors in the order red, white, and blue
        """
        # 0 pass
        write = 0
        read = 0
        while read<len(nums): # 读写双指针用while...
            if nums[read]==0:
                tmp = nums[write]
                nums[write] = nums[read]
                nums[read] = tmp
                write+=1
            else:
                read+=1
        # print(nums)
        read=write
        while read<len(nums): # 读写双指针用while...
            if nums[read]==1:
                tmp = nums[write]
                nums[write] = nums[read]
                nums[read] = tmp
                write+=1
            else:
                read+=1
        read=write
        while read<len(nums) and write<len(nums): # 读写双指针用while...
            if nums[read]==2:
                tmp = nums[write]
                nums[write] = nums[read]
                nums[read] = tmp
                write+=1
            else:
                read+=1
        
