class Solution:
    def moveZeroes(self, nums: list[int]) -> None:
        """
        读写分离双指针
        """
        r=0
        w=0
        while r!=len(nums):
            if nums[r]!=0:
                tmp = nums[w]
                nums[w]=nums[r]
                # w被swap过来的一定是0，或者w==r，不用看，但需要交换到后面
                nums[r]=tmp
                w+=1
            r+=1