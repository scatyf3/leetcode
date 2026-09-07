class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()                                   # ← 一切的前提
        n = len(nums)
        res = []

        for i in range(n - 2):
            if nums[i] > 0:                           # 剪枝: 最小的都 > 0, 三个正数凑不出 0
                break
            if i > 0 and nums[i] == nums[i - 1]:      # 去重①: 第一个数跳过相邻重复
                continue

            l, r = i + 1, n - 1                       # 下标天然满足 i < l < r, 不可能重合
            while l < r:
                total = nums[i] + nums[l] + nums[r]
                if total < 0:
                    l += 1                            # 和偏小 -> 左指针右移(取更大的数)
                elif total > 0:
                    r -= 1                            # 和偏大 -> 右指针左移(取更小的数)
                else:
                    res.append([nums[i], nums[l], nums[r]])
                    l += 1
                    while l < r and nums[l] == nums[l - 1]:   # 去重②: 跳过和上一个相同的左值
                        l += 1
                    # 只跳 l 就够: 第一个数和左值都定了, 右值唯一, 不会再产出重复三元组
        return res
