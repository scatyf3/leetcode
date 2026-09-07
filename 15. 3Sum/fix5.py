class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        n = len(nums)
        res = []
        nums.sort()                                   # 去重① 和剪枝都依赖它
        for fix_start in range(n - 2):
            # we need at least 2 elem for inner interations
            if nums[fix_start] > 0:                   # 剪枝: 最小的都 > 0, 三个正数凑不出 0
                break
            if fix_start and nums[fix_start] == nums[fix_start - 1]:
                continue                              # 去重①: 跨 fix_start, 和左邻居比 -> 保留第一份

            remain_map = {}                           # remain -> index (index 其实没用到, set 也行)
            dup = set()                               # 去重②: 同一个 fix_start 内已收过的 nums[i]
            target = 0 - nums[fix_start]
            for i in range(fix_start + 1, n):         # 这里要 +1 否则 nums[fix_start] 会被自己复用
                if nums[i] in remain_map and nums[i] not in dup:
                    res.append([nums[fix_start], target - nums[i], nums[i]])
                    dup.add(nums[i])
                remain = target - nums[i]
                remain_map[remain] = i
        return res
