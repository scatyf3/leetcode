class Solution:
    def generateParenthesis(self, n: int) -> list[str]:
        res=[]
        cur_slice=[]

        def dfs(cur_slice,left_remain,right_remain):
            if left_remain==0 and right_remain==0:
                res.append("".join(cur_slice))
            if left_remain>0:
                cur_slice.append("(")
                dfs(cur_slice,left_remain-1,right_remain)
                cur_slice.pop()
            if right_remain>left_remain:
                cur_slice.append(")")
                dfs(cur_slice,left_remain,right_remain-1)
                cur_slice.pop()

        dfs(cur_slice,n,n)
        return res
        