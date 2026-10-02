class Solution:
    def subsetsWithDup(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
        res = []
        cur = []
        seen = set()

        def dfs(cur_index):
            s = str(cur)
            if s not in seen:
                res.append(cur[:])
                seen.add(s)
            for i in range(cur_index,len(nums)):
                cur.append(nums[i])
                dfs(i+1)
                cur.pop()
        dfs(0)
        return res

                