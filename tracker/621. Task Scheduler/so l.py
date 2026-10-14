import heapq
from collections import Counter, deque

class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:
        # heap里存的是可以被lauch的task，ready
        heap = [-c for c in Counter(tasks).values()]  
        heapq.heapify(heap)
        q = deque()  # (剩余次数的负数, 回 heap 的时刻)
        t = 0
        while heap or q:
            t += 1
            if heap:
                c = heapq.heappop(heap) + 1  # 从heap中拿出一个元素，counter-1
                if c:                        # 如果当前task还有需要跑的
                    q.append((c, t + n))     # 第 t+n 格结束冷却 回 heap
            else:
                t = q[0][1]                  # 如果heap里没东西，直接放置空转，跳到队头对应的时间，sim的省略
            if q and q[0][1] == t:           # 队头冷却完，放回 heap
                heapq.heappush(heap, q.popleft()[0])
        return t
