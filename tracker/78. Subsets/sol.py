class Solution:
    def subsets(self, nums: list[int]) -> list[list[int]]:
        res = []
        cur = []
        def dfs(cur, start):
            # 决策树上每个节点都是一个合法子集, 进来就收
            res.append(cur[:])
            # start: 只能从 start 往后挑下一个元素, 保证不重复
            for idx in range(start, len(nums)):
                cur.append(nums[idx])
                dfs(cur, idx + 1)
                cur.pop()
        dfs(cur, 0)
        return res


if __name__ == "__main__":
    s = Solution()
    print(s.subsets([1, 2, 3]))
    print(s.subsets([0]))
