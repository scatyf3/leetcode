class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        intervals.sort(key=lambda x:x[1])
        # print(intervals) sort by end
        res = []
        remove=0 #minimal

        for interval in intervals:
            # interval.start < res.end => overlap
            if res and interval[0]<res[-1][1]:
                remove+=1
            else:
                res.append(interval)
        return remove
