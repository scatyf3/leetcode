class Solution:
    def majorityElement(self, nums: list[int]) -> list[int]:
        # naive -> scan via cnt
        n=len(nums)
        threshold = n//3
        cnt = Counter()
        res=set()
        for elem in nums:
            cnt[elem]+=1
            if elem not in res and cnt[elem]>threshold:
                res.add(elem)
        return list(res)