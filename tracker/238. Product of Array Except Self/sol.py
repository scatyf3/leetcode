from typing import List


class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        '''
        answer[i] = (i 左边所有数的积) × (i 右边所有数的积)
        两趟递推, 0 自动传播, 不需要任何特判。
        follow up: 输出数组不算额外空间 -> 前缀积直接写进 res, 后缀积用一个标量从右往左滚。
        '''
        # TODO: 自己写
        pass


# ============================================================
# 附: 除法路线, 两版。题目明确写了 without division, 这里只做错题记录
# ============================================================
#
# 第一反应的思路原文:
#     1d dp for partial sum?
#     no, mul is reversable, thus just get global prod and div nums[i]
#     the hard part is to handle 0 correctly
#
# 「0 很难处理」正是题目想让你放弃除法的信号。
#
#
# ---- WA 版 -------------------------------------------------
#
# class Solution:
#     def productExceptSelf(self, nums: List[int]) -> List[int]:
#         n = len(nums)
#         global_prod = 1
#         zero_index = set()
#         res = [0 for i in range(n)]
#         for i in range(n):
#             if nums[i] != 0:
#                 global_prod = global_prod * nums[i]
#             else:
#                 zero_index.add(i)
#         if len(zero_index) == len(nums):        # ← 坑 1: 只兜住了「全是 0」
#             return res
#         if len(zero_index) != 0:
#             for idx in range(n):
#                 if idx in zero_index:
#                     res[idx] = int(global_prod)
#                 else:
#                     res[idx] = 0
#         else:
#             for idx in range(n):
#                 res[idx] = int(global_prod / nums[idx])   # ← 坑 2: 浮点除
#         return res
#
# 坑 1: nums = [0, 0, 1] -> 返回 [1, 1, 0], 期望 [0, 0, 0]。
#       zero_index = {0, 1}, len 2 != 3 所以没短路, 两个 0 位都填了 global_prod = 1。
# 坑 2: int(a / b) 走浮点, 大乘积掉精度; 负数还朝 0 截断而不是向下取整。该用 //。
#
#
# ---- 修好 0 之后 -------------------------------------------
#
# 关键: 答案的形状只由 0 的个数决定, 跟 0 在哪没关系。所以是三档, 不是两档。
#
#     zero_cnt == 0   ->  res[i] = prod // nums[i]
#     zero_cnt == 1   ->  只有那个 0 的位置 = 其余非零元素的积, 其他位置全 0
#     zero_cnt >= 2   ->  全 0 (任何位置都至少还剩一个 0 在乘)
#
# class SolutionDiv:
#     def productExceptSelf(self, nums: List[int]) -> List[int]:
#         n = len(nums)
#         res = [0] * n
#         prod = 1                       # 非零元素的积
#         zero_cnt = 0
#         zero_idx = -1
#         for i, v in enumerate(nums):
#             if v == 0:
#                 zero_cnt += 1
#                 zero_idx = i
#             else:
#                 prod *= v
#         if zero_cnt >= 2:              # ★ 原来写的是 == len(nums), 漏了中间档
#             return res
#         if zero_cnt == 1:
#             res[zero_idx] = prod
#             return res
#         for i, v in enumerate(nums):
#             res[i] = prod // v         # ★ // 不是 /; v 已保证非零
#         return res
#
# 可迁移: 分类讨论要按「决定答案的那个量」分档 (这里是 0 的个数),
#         而不是按顺手写得出来的条件 (全 0 / 非全 0)。顺手的条件往往漏中间档。
