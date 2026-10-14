class Solution:
    def findMin(self, nums: List[int]) -> int:
        l, r = 0, len(nums) - 1
        while l < r:
            if nums[l] < nums[r]:      # 我们的切片已经是升序，已经找到原始的起点，直接返回l
                return nums[l]
            mid = (l + r) // 2
            if nums[mid] > nums[r]:
                l = mid + 1            # mid 比某个元素大 -> 它一定不是最小 -> 可以排除
            else:
                r = mid                # mid 自己可能就是最小 -> 只能收到 mid, 不能 mid-1
        return nums[l]
