class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        res = set()
        n = len(nums)
        for i in range(n):
            seen = set()                          # 只装本轮 i 已经走过的 nums[j]
            for j in range(i + 1, n):
                c = -(nums[i] + nums[j])          # 需要的第三个数
                if c in seen:                     # ← 必须先查
                    res.add(tuple(sorted((nums[i], nums[j], c))))   # 规范化后进 set 去重
                seen.add(nums[j])                 # ← 再把自己加进去
        return [list(t) for t in res]
