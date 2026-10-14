from typing import List


class Solution:
    '''
    sol2_naive_ps.py 的修正版。思路一模一样 —— 前缀积 / 后缀积各一个数组,
    两个数组都取 n+1 长, 多出来的那格放「空积」1, 靠错位避开 i=0 / i=n-1 的特判。
    只改了 suffix 的填法, 见文件底部。

    O(n) time, O(n) extra space。
    '''

    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)

        # prefix[i] = nums[0..i-1] 的积, prefix[0] = 1 (空积)
        prefix_mul = [1] * (n + 1)
        for i in range(n):
            prefix_mul[i + 1] = prefix_mul[i] * nums[i]

        # suffix[i] = nums[i..n-1] 的积, suffix[n] = 1 (空积)
        # ★ 预分配好位置, 从右往左写格子; 不用 insert(0, ...)
        suffix_mul = [1] * (n + 1)
        for i in range(n - 1, -1, -1):
            suffix_mul[i] = suffix_mul[i + 1] * nums[i]

        # nums   =        [ 1,  2,  3,  4]
        # prefix = [ 1,  1,  2,  6, 24]        错开一格: prefix[i] 不含 nums[i]
        # suffix =     [24, 24, 12,  4,  1]    错开一格: suffix[i+1] 不含 nums[i]
        # res    =        [24, 12,  8,  6]
        #
        # 「掐头去尾」就是这个错位: prefix 的最后一格和 suffix 的第一格
        # 都等于全体乘积, 谁都用不上。
        return [prefix_mul[i] * suffix_mul[i + 1] for i in range(n)]


# ============================================================
# 跟 sol2_naive_ps.py 的唯一区别: suffix 的填法
#
#     # naive 版, 结果对但会 TLE
#     suffix_mul = [1]
#     for i in range(n):
#         suffix_mul.insert(0, suffix_mul[0] * nums[n - i - 1])
#
# list.insert(0, x) 要把已有元素整体后挪一格, 单次 O(k), n 次累计 O(n^2)。
# 实测 n = 1e5 全 1 的输入: insert 版 4.12s, 预分配倒着写 0.017s。
#
# 想保留 append 的手感也行: 正着 append 完最后 reverse 一次, 同样是 O(n)。
#
# > 递推方向和存储方向不一致时, 别用 insert(0) 去凑。
# > 要么预分配好长度按下标倒着写, 要么 append 完再 reverse。
# ============================================================
