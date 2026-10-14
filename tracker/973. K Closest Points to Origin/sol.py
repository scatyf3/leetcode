class Solution:
    def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:
        # heap: [distance,[x,y]]
        # Closest - minimal heap
        h=[]

        for point in points:
            distance=sqrt(point[0]**2+point[1]**2)
            elem = [distance,point]
            heapq.heappush(h,elem)
        
        res=[]
        for i in range(k):
            elem=heapq.heappop(h)
            res.append(elem[1])
        return res
        