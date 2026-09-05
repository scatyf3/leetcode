# 第一版尝试, WA(6 个用例全错)。根子上只有一个错: dp 的初值。
# 定义 dp[i] = 以 nums[i] 结尾的最长上升子序列长度 -> 至少是它自己, 初值必须是 1。
# 初值写错之后, 下面三处全是在替它擦屁股, 而且越擦越错:
#   1. dp[0] = 0        -> 应该是 1(长度 0 却以 nums[0] 结尾, 自相矛盾); n=0 时还会 IndexError
#   2. dp[j] != 1       -> 致命。dp[j]==1 表示"j 自己单独一条", dp[j]+1 正是想要的长度 2,
#                          排除掉它 [1,2] 就永远接不上, 答案退化成 1
#   3. dp = [-114]*n    -> i>=1 的 dp[i] 从没赋初值, 没有 j 命中时哨兵会被 max 传染出去
#   4. mx=0 且 i 从 1 开始 -> n==1 时循环一次不进, 返回 0
# 正确写法见 sol2.py: dp = [1]*n, 零个 if。
# 规矩: 初始化 = 把定义作用在"最小情形"上; 发现自己在加特判, 多半是初值设错了。
#       (同 notes/sliding-window-template.md 的「起始状态怎么想」)

class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        '''
        并非双指针，可以跳选，subseq是cs固定的描述「可跳跃的子切片」的术语
        这里是dp？，存「截止到当前index最大递增序列」 的长度
        dp[i] = 以 nums[i] 结尾的最长上升子序列长度 ✓

        '''
        n = len(nums)
        dp=[-114 for i in range(n)]
        dp[0]=0 # 这里写0还是1
        mx = 0
        for i in range(1,n):
            for j in range(0,i): # 考虑全部前面的元素，选最大的
                if nums[i]>nums[j] and dp[j]!=1:
                    dp[i]=max(dp[i],dp[j]+1) # 选中j作为prefix，但是要处理 真prefix还是单独作为1
            mx = max(mx,dp[i])
        return mx

'''
实测(全 WA):
  [10,9,2,5,3,7,101,18] -> 1   期望 4
  [0,1,0,3,2,3]         -> 1   期望 4
  [7,7,7,7]             -> 0   期望 1
  [1]                   -> 0   期望 1
  [1,2]                 -> 1   期望 2
'''
