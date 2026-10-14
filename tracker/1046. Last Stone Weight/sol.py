class Solution:
    def lastStoneWeight(self, stones: List[int]) -> int:
        h = []
        # store - weight

        for stone in stones:
            heapq.heappush(h,-stone)

        while len(h)>1:
            stone_1=heapq.heappop(h) # larger
            stone_2=heapq.heappop(h)
            if stone_1!=stone_2:
                res = stone_1-stone_2
                heapq.heappush(h,res)
        if len(h)>0:
            return -h[0]
        else:
            return 0
''' 
[114,114]
'''