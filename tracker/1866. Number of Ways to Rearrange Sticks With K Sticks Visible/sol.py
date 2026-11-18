class Solution:
    def rearrangeSticks(self, n: int, k: int) -> int:
        MOD = 10**9 + 7
        # dp[sticks][seen] = 用 sticks 根木棍、看得见 seen 根的排法数
        dp = [[0] * (k + 1) for _ in range(n + 1)]
        dp[0][0] = 1

        for sticks in range(1, n + 1):
            for seen in range(1, min(k, sticks) + 1):
                shortest_first = dp[sticks - 1][seen - 1]               # 最矮的单独一组，排最左边，看得见
                shortest_hidden = (sticks - 1) * dp[sticks - 1][seen]   # 最矮的插在别人后面，被挡住
                dp[sticks][seen] = (shortest_first + shortest_hidden) % MOD
        return dp[n][k]
