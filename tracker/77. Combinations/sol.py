class Solution:
    def combine(self, n: int, k: int) -> list[list[int]]:
        # c4 2
        # backtrack
        res = []
        cur = []
        def dfs(cur_n,cur_k):
            if cur_k>=k:
                res.append(cur[:])
                return
            for next_number in range(cur_n,n+1):
                cur.append(next_number)
                dfs(next_number+1,cur_k+1)
                cur.pop()
        dfs(1,0)  
        return res


        