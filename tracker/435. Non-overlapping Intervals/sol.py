class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        intervals.sort(key=lambda x: x[1]) # 按照end排序
        count, end = 0, float('-inf')  # end是current end
        for s, e in intervals: # 对每个slice
            if s>=end:
                end=e
                count+=1
        return len(intervals) - count

            