class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        # heap
        # hash? to get (elem,freq) and convert to   (freq,elem)
        cnt = Counter()
        for elem in nums:
            cnt[elem]+=1
        hp = []
        for key in cnt:
            heapq.heappush(hp,(-cnt[key],key))
            # python has min heap only
        res = []
        for i in range(k):
            res.append(heapq.heappop(hp)[1])
        return res