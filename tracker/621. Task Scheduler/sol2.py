import heapq
from collections import Counter, deque

class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:
        # counter heap for max: launch more counter task first
        heap = [-c for c in Counter(tasks).values()]  
        heapq.heapify(heap)
        q = deque()  # (剩余次数的负数, 回 heap 的时刻)
        t = 0
        while heap or q: # still have task
            if heap:
                counter = heapq.heappop(heap)
            counter+=1
            if counter<0:
                q.append((counter,t+n+1)) # time to return
            t+=1
            while q and q[0][1]<=t:
                counter,_ = q.popleft()
                heapq.heappush(heap,counter)
            #print(heap)
            #print(q)

        return t

            