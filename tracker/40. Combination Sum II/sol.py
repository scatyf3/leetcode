class Solution:
    def combinationSum2(self, candidates: list[int], target: int) -> list[list[int]]:
        candidates.sort()
        res = []
        cur = []
        def dfs(cur_idx,cur_val):
            if cur_val==0:
                res.append(cur[:])
            for i in range(cur_idx,len(candidates)):
                # cur_val-candidates[i]>=0 : valid
                # i == cur_idx or candidates[i] != candidates[i-1]
                # 1. i-1 就是上一个被选的元素，已经选了
                # 要么值和前一个不同，可以直接选；要么值相同，但前一个已经被选了
                # i == cur_idx 意味着是选择后下一个元素，即前一个数值被选中，如果连着，则不用考虑重复，不连着要考虑
                if cur_val-candidates[i]>=0 and (i == cur_idx or candidates[i] != candidates[i-1]):
                    cur.append(candidates[i])
                    # how to remove dup correctly
                    # 若要连续，如1 valid可以是 0，也可以是01，不可以是1
                    dfs(i+1,cur_val-candidates[i])
                    cur.pop()
        dfs(0,target)
        return res

            