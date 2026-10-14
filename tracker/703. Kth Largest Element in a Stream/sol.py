class KthLargest:

    def __init__(self, k: int, nums: List[int]):
        '''
        [4, 5, 8, 2]

        min heap
        '''
        self.h = []
        self.k = k
        if k>=len(nums):
            for elem in nums:
                heapq.heappush(self.h,elem)
        else:
            for i in range(k):
                heapq.heappush(self.h,nums[i])
            for i in range(k,len(nums)):
                if self.h[0] < nums[i]:
                    heapq.heappop(self.h)
                    heapq.heappush(self.h,nums[i])

    def add(self, val: int) -> int:
        if len(self.h)==0:
            heapq.heappush(self.h,val)
            return val
        if self.h[0] < val:
            res = heapq.heappop(self.h)
            heapq.heappush(self.h,val)
        res = self.h[0]
        return res
        