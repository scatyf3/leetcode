class Solution:
    def longestValidParentheses(self, s: str) -> int:
        # given 思路是dp，怎么处理？
        # dp[i] 是 以 s[i] 结尾的最长有效子串长度。
        # ( => 继承之前的
        # ) => 结算一些东西， () 和)), 找前面第一个( ? 
        # stk存等待配对左括号index

        dp = [0 for i in range(len(s)+1)]
        stk = []

        for i in range(len(s)):
            dp_idx = i+1
            if s[i]=="(":
                dp[dp_idx]=0
                # stk.clear()
                stk.append(i)
            else: # )
                if stk: # matched
                    prev_idx = stk.pop()
                    dp[dp_idx] = (i - prev_idx + 1) // 2 + dp[prev_idx]
                    # 只要栈顶有东西，就一定valid，从而之前的也是valid的
            # print(dp)
            # print(stk)
        return max(dp)* 2 # we count pair but result need number of valid ()
                
