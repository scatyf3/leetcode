class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        # O(n)
        # step1: build a hash table key:elem value: next elem, graph; find start
        # step2: iterate through hash table, key,record max len and visited node
        # wait what we can build set using api directly
        s = set(nums)
        # 第一遍:挑出所有链头, 这里的diff是需要所有start
        starts = [x for x in s if x - 1 not in s]
        # 第二遍:每条链走一次
        best = 0
        for x in starts:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
        return best
    