class Solution:
    def combinationSum2(self, candidates: list[int], target: int) -> list[list[int]]:
        candidates.sort()
        res = []
        cur = []
        def dfs(start_idx,remain):
            if remain==0:
                res.append(cur[:])
            for idx in range(start_idx,len(candidates)):
                # 这里就是处理下edgecase
                # idx > start_idx说明这一层的 for 循环已经试过至少一个兄弟分支了
                # 当前这个不是本层的第一个选择，只有此时才会有重复
                # 如果无，则[1,1,1,1],  correct→ [[1,1]] 删掉`idx > start_idx` →  []
                if idx > start_idx and candidates[idx] == candidates[idx-1]:
                    continue 
                if candidates[idx]<=remain : # skip dup via (len(cur)!=0 and cur[-1]!=candidates[idx])?
                    cur.append(candidates[idx])
                    dfs(idx+1,remain-candidates[idx]) # cannot be repeat, cannot be dup
                    cur.pop()
        dfs(0,target)
        return res