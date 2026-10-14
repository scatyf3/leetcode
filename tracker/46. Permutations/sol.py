class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        res, cur = [], []
        cand = set(nums)

        def dfs():
            if not cand:                    # 1. 空了才是到底
                res.append(cur[:])
                return
            for num in list(cand):          # 3. 先拷一份快照再迭代，这里迭代copy，修改原品
                cand.remove(num); cur.append(num)    # 选：两份状态一起改
                dfs()
                cur.pop(); cand.add(num)             # 撤：两份状态一起还原
        dfs()
        return res
