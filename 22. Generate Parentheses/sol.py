class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        cur_state = []
        res = []
        self.dfs(res, cur_state, n, n)         
        res_str = []
        for sub_lst in res:
            res_str.append("".join(sub_lst))
        return res_str                          

    def dfs(self, res, cur_state, left_remain, right_remain):   
        if left_remain == 0 and right_remain == 0:
            res.append(cur_state[:]) # append copy
            return 

        if left_remain>0:
            cur_state.append("(")
            self.dfs(res, cur_state, left_remain - 1, right_remain)
            cur_state.pop()
        if right_remain>0 and left_remain<right_remain: # left_remain>=right_remain means invalid, () or x, we can only place an (
            cur_state.append(")")
            self.dfs(res, cur_state, left_remain, right_remain-1)
            cur_state.pop()
