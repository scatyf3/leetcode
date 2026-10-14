class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        n = len(nums)
        f = [0] * n          # f[i] = 以 i 结尾的子数组里, 最大的乘积
        g = [0] * n          # g[i] = 以 i 结尾的子数组里, 最小的乘积
        f[0] = g[0] = nums[0]

        for i in range(1, n):
            x = nums[i]
            f[i] = max(x, f[i-1] * x, g[i-1] * x)      # 三个候选取最大
            g[i] = min(x, f[i-1] * x, g[i-1] * x)      # 同样三个候选取最小
        return max(f)

    
'''
error solution:
double pointer/dp 🤔, because extend double pointer do not gradteee find better result
dp[l][r] = max(nums[l-1]* dp[l-1][r],nums[r+1]* dp[l][r+1])

1. 这里我们只需要写记录一维状态，退化成贪心，这里遍历 数组
2. 决策是，我们已知上一个位置结尾最大的乘积，那当前位置最大乘积到底是切割之前的，还是继续保留，若保留，则当前情况是负负得正好，还是继续正数好
3. 一个优化就是删掉数组，迭代的时候贪心找best即可，但对时间复杂度没啥影响

省数组版
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        best = mx = mn = nums[0]      # mx/mn: 以当前位置结尾的最大 / 最小乘积
        for x in nums[1:]:
            cand = (x, mx * x, mn * x)     # 三选一: 重新起头 / 接在最大后面 / 接在最小后面
            mx, mn = max(cand), min(cand)  # 必须同时更新, 不能先算 mx 再用新 mx 算 mn
            best = max(best, mx)
        return best

'''
