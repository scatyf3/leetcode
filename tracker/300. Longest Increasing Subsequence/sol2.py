# 我自己那版的最小修正 —— 保留原来的形状(i 从 1 开始 + mx 累加器), 只改初值。
# 改动就三处, 全是同一个根因(dp 的初值应该是 1):
#   dp=[-114]*n; dp[0]=0   ->  dp=[1]*n     以 i 结尾, 至少是它自己
#   mx = 0                 ->  mx = 1       n==1 时循环一次不进, 直接返回初值, 所以初值就得是答案
#   and dp[j]!=1           ->  删掉         dp[j]==1 是"j 自己单独一条", dp[j]+1 正是想要的长度 2
# 标准写法(i 从 0 开始, return max(dp))见 sol.py, 两者等价。

class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        '''
        并非双指针，可以跳选，subseq是cs固定的描述「可跳跃的子切片」的术语
        dp[i] = 以 nums[i] 结尾的最长上升子序列长度
        答案不是 dp[-1] 而是所有 dp[i] 的最大值 —— 终点不固定, 最优解可以在任何位置结尾
        '''
        n = len(nums)
        dp = [1] * n              # 每个 i 都至少是 1, 不只是 dp[0]
        mx = 1                    # n==1 时循环不进, 返回值就是这个初值
        for i in range(1, n):
            for j in range(0, i):             # 考虑全部前面的元素，选最大的
                if nums[i] > nums[j]:         # j 能接到 i 前面
                    dp[i] = max(dp[i], dp[j] + 1)
            mx = max(mx, dp[i])
        return mx
