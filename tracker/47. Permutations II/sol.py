class Solution:
    def permuteUnique(self, nums: list[int]) -> list[list[int]]:
        res = []
        cur = []

        def dfs(remain,cur):
            if sum(remain.values())==0: # all zeros
                #print(remain)
                #print(cur)
                res.append(cur[:])
            for elem in remain:
                if remain[elem]>0:
                    remain[elem]-=1
                    cur.append(elem)
                    #print(remain)
                    #print(cur)
                    dfs(remain,cur)
                    remain[elem]+=1
                    cur.pop()
        st_nums = Counter(nums) # shoule be counter
        dfs(st_nums,cur)  
        return res      