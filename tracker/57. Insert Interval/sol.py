class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        # given a interval, merge to an existing interval list
        # merge all interval的弱化版
        intervals.append(newInterval)
        intervals.sort()
        res = []
        for interval in intervals:
            # res.end >=interval.start => overlap => merge
            if res and res[-1][1]>=interval[0]:
                res[-1][0]=min(res[-1][0],interval[0])
                res[-1][1]=max(res[-1][1],interval[1])
            else:
                res.append(interval)
        return res