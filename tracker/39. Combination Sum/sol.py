class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        res = []
        cur = []

        def dfs(candidate,remain):
            if remain==0:
                res.append(cur[:])

            for i in range(candidate,len(candidates)):
                if candidates[i]<=remain:
                    cur.append(candidates[i])
                    dfs(i,remain-candidates[i])
                    cur.pop()

        dfs(0,target)
        return res
