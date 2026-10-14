class MedianFinder:
    # naive way: insert each time, self list is ordered
    # but we do not care about full order, we only care about partial order

    def __init__(self):
        self.min_heap=[]
        self.max_heap=[]
        self.size = 0 # 0-> to min, else to max
    
    def _rebalance(self):
        # eg 2 -> min, 3 -> max, 4->min, currenly is not balance
        # python heap is always min heap, thus min_heap store negative to get max value
        if self.size>=2:
            min_max = -heapq.heappop(self.min_heap)
            max_min = heapq.heappop(self.max_heap)
            if min_max>max_min: # inbalance
                heapq.heappush(self.max_heap,min_max)
                heapq.heappush(self.min_heap,-max_min)
            else: # just put it back
                heapq.heappush(self.max_heap,max_min)
                heapq.heappush(self.min_heap,-min_max)

    def addNum(self, num: int) -> None:
        if self.size%2==0:
            heapq.heappush(self.min_heap,-num)
        else:
            heapq.heappush(self.max_heap,num)
        self.size+=1
        self._rebalance()

    def findMedian(self) -> float:
        if self.size%2==0:
            return (self.max_heap[0]-self.min_heap[0])/2
        else:
            return -self.min_heap[0]
        