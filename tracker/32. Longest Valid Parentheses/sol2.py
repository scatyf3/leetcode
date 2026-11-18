class Solution:
    def longestValidParentheses(self, s: str) -> int:
        stk = [-1]                   # 栈顶始终是「最近一个没被匹配的位置」
        res = 0
        for i, c in enumerate(s):
            if c == "(":
                stk.append(i)
            else:
                stk.pop()
                if not stk:          # 这个 ')' 没配上，它成为新的边界
                    stk.append(i)
                else:
                    res = max(res, i - stk[-1])
        return res