class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        res = [1] * n

        p = 1
        for i in range(n):
            res[i] = p          # 先用
            p *= nums[i]        # 后更新

        s = 1
        for i in range(n - 1, -1, -1):
            res[i] *= s         # 先用
            s *= nums[i]        # 后更新

        return res
