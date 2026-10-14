class Solution:
    def jump(self, nums: list[int]) -> int:
        n = len(nums)
        l, r = 0, 0          # 当前层 = 下标区间 [l, r]
        jumps = 0
        while r < n - 1:     # 当前层还没覆盖终点
            farthest = max(i + nums[i] for i in range(l, r + 1))
            l, r = r + 1, farthest   # 下一层 = [r+1, farthest]
            jumps += 1
        return jumps

