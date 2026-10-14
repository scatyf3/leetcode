class Solution:
    def longestValidParentheses(self, s: str) -> int:
        n = len(s)
        dp = [0] * n                      # dp[i] = 以 s[i] 结尾的最长合法子串长度

        def at(k):                        # 越界当 0，防止 dp[-1] 悄悄取到最后一个
            return dp[k] if k >= 0 else 0

        for i in range(1, n):
            if s[i] == '(':
                continue
            if s[i-1] == '(':             # 情况 1：...()
                dp[i] = 2 + at(i - 2)
            else:                         # 情况 2：...))
                j = i - dp[i-1] - 1       # 跳过中间那段，j 是和 s[i] 配对的候选
                if j >= 0 and s[j] == '(':
                    dp[i] = dp[i-1] + 2 + at(j - 1)
        return max(dp, default=0)
