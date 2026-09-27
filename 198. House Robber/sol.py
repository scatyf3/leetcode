# ---------- v1: 我自己写的(三处特判) ----------
class SolutionV1:
    def rob(self, nums: list[int]) -> int:
        # can't rob adjacent house
        dp = [0 for i in range(len(nums))]  # rob here current max
        if(len(nums)==0):
            return 0
        if(len(nums)==1):
            return nums[0]
        dp[0]=nums[0]
        dp[1]=max(nums[1],nums[0])
        for i in range(2,len(nums)):
            dp[i]=max(dp[i-1],nums[i]+dp[i-2])
        return max(dp[len(nums)-1],dp[len(nums)-2])
        # 三处特判同一个根: dp[i] = 「以第 i 间结尾」, base 落在真实数据上,
        # dp[0]=nums[0] 要求至少 1 个元素、dp[1] 要求至少 2 个。
        # 末尾 max(dp[-1],dp[-2]) 是多余的: dp[i]=max(dp[i-1],...) 保证单调不减。


# ---------- v2: B 类口径 + 滚动压缩(零特判) ----------
class Solution:
    def rob(self, nums: list[int]) -> int:
        '''
        Input:
        - nums: list[int], 1 <= len <= 100, 0 <= nums[i] <= 400
        Target: 选一个两两不相邻的下标集合, 使总和最大
        Return: 最大总金额
        Output: int

        解法: 1d DP, B 类口径 + 滚动压缩   O(n) 时间 / O(1) 空间

          dp[i] = **前 i 间房**的最优值 (不是「以第 i 间结尾」)
          转移   dp[i] = max(dp[i-1], dp[i-2] + nums[i-1])
          base   dp[0] = 0          # 空集, 不看数据就能写出来 -> 两个 len 特判消失
          答案   dp[n]              # B 类口径, 就是最后一格

        依赖窗口 k=2 是常数 -> 两个标量, 数组不用开。判据见 paradigms/1d-dp.md §2 §5。
        '''
        prev2, prev1 = 0, 0                                # dp[i-2], dp[i-1]
        for x in nums:
            prev2, prev1 = prev1, max(prev1, prev2 + x)    # 右边全是旧值, 同时更新
        return prev1

        '''
        调试期想留数组(能看出哪格开始错), 代价是表比数据长一格:
            dp = [0] * (n + 1)
            for i in range(1, n + 1):
                dp[i] = max(dp[i-1], (dp[i-2] if i >= 2 else 0) + nums[i-1])
            return dp[n]

        Test Cases:
        [1,2,3,1]        -> 4    偷 1+3, 不是相邻的 2+1
        [2,7,9,3,1]      -> 12   偷 2+9+1, 先拿最大的 9 再拿两边会漏
        [2,1,1,2]        -> 4    偷首尾。奇偶下标分别求和都只有 3, 「隔一间偷」是错的
        [5]              -> 5    n=1, v1 要特判
        [0]              -> 0
        [6,1,1,6,1,6]    -> 18   选 0,3,5: 先跳三格再跳两格, 步长不固定
        [100,1,1,100]    -> 200
        '''
