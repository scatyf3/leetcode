class Solution:
    def coinChange(self, coins: list[int], amount: int) -> int:
        # greedy？不知道有没有性质，否 6 [5,3,2]，如果先greedy选5就错了
        # 回溯拿到解答列表，然后select min len => 肯定 不最优
        # 或者在回溯从大往小搜，搜到了就返回？ => 仍然不贪心， 6 [4,3,1]，这里先extend4，则4，1，1并非最优

        # dp, 1d dp，index的含义是「多少💰的最小solution」
        dp = [-1 for i in range(amount+1)]
        dp[0]=0
        for i in range(1,amount+1): #0不参与啊，如果考虑0，则 全都被+inf覆盖了
            cur_min_coin=float("+inf")
            for coin in coins:
                if i-coin>=0:
                    cur_min_coin=min(cur_min_coin,dp[i-coin]+1)
            dp[i]=cur_min_coin
        # print(dp)
        if dp[amount]==float("+inf"):
            return -1
        else:
            return dp[amount]
            