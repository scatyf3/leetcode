    '''
    if insert, l or right
    move index, insert val, update curr median

    思路: 维护一个始终有序的数组。二分找到插入位置,插进去,
          再更新中位数下标。addNum O(n) (insert 要挪元素), findMedian O(1)。
    '''

    def __init__(self):
        self.n = 0
        self.min_part_h = [] # store - act as max stack
        self.max_part_h = [] # original min stack
        self.min_len=0
        self.max_len=0

    def addNum(self, num: int) -> None:
        # insert according to heaplen
        if self.min_len==self.max_len:
            heapq.heappush(self.min_part_h,-num)
            self.min_len+=1
        elif self.min_len==self.max_len+1:
            heapq.heappush(self.max_part_h,num)
            self.max_len+=1
        else: 
            print("error")
        # check rebalance
        if self.need_rebalance():
            self.rebalance()
        # print(self.min_part_h)
        # print(self.max_part_h)

    def findMedian(self) -> float:
        if self.min_len==self.max_len:
            min_max = - self.min_part_h[0]
            max_min = self.max_part_h[0]
            avg = (min_max+max_min)/2
            return avg
        else:
            min_max = - self.min_part_h[0]
            return min_max
    
    def need_rebalance(self):
        if len(self.min_part_h)!=0 and len(self.max_part_h)!=0:
            if -self.min_part_h[0] > self.max_part_h[0]:
                return True
            else:
                return False
        else:
            return False

    def rebalance(self):
        # do not touch len, touch value only
        # the invalid one must be min and only need 1 step
        balance_value = -heapq.heappop(self.min_part_h)
        heapq.heappush(self.max_part_h,balance_value)
        balance_value = heapq.heappop(self.max_part_h)
        heapq.heappush(self.min_part_h,-balance_value)