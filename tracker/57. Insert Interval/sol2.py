class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        res = []
        i, n = 0, len(intervals)
        s, e = newInterval  # 中间段会把 s, e 往外撑

        # 1. 左段：完全在 new 左边，原样放进 res
        while i < n and intervals[i][1]<s:
            res.append(intervals[i])
            i += 1

        # 2. 中间段：和 new 有重叠，撑大 [s, e]
        # interval.end>newi.s
        # interval.s<newi.e
        while i < n and intervals[i][1]>=s and intervals[i][0]<=e:
            s = min(intervals[i][0],s)
            e = max(intervals[i][1],e)
            i += 1
        res.append([s, e])

        # 3. 右段：剩下的全部原样接上
        while i < n and intervals[i][0]>e:
            res.append(intervals[i])
            i+=1

        return res
