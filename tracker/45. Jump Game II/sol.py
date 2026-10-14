class Solution:
    def jump(self, nums: list[int]) -> int:
        '''
        # Each element nums[i] represents the maximum length of a forward jump from index i.
        # Return the minimum number of jumps to reach index n - 1.

        1d dp或者 graph？需要一个preprocess的reach array，每个index迭代找最小
        nums = [2,3,1,1,4]
        path1: 0 -> 2 ->3 -> 4
        path2: 0 -> 1 -> 4(optimal)
        reacable:
        {
            0:
            1:0
            2:0,1
            3:1,2
            4:1,3
        }
        然后每个位置反查这个表

        但这个表如何构建？
        '''
        reachable = {}
        for index in range(len(nums)):
            cur_val = nums[index]
            for next_idx in range(index+1,min(cur_val+index+1,len(nums))):
                if next_idx not in reachable:
                    reachable[next_idx]=[index]
                else:
                    reachable[next_idx].append(index)
        # print(reachable)
        dp = [len(nums) for _ in range(len(nums))]
        dp[0]=0
        for index in range(1,len(nums)):
            reach_prefix = reachable[index]
            res = float("+inf")
            for prefix in reach_prefix:
                res = min(res,dp[prefix]+1)
            dp[index]=res
        # print(dp)
        return dp[len(nums)-1]
            
