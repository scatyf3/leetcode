class Solution:
    def minMeetingRooms(self, intervals: list[list[int]]) -> int:
        starts = sorted([interval[0] for interval in intervals])
        ends = sorted([interval[1] for interval in intervals])

        res = cur = 0
        j = 0                       # 指向下一个还没处理的结束时间
        for s in starts: # 迭代每个start，这是cur正变化的地方
            # 迭代j，检查每个小于s的end有没有被cancel
            # j往前走，每次从上次的checkpoint之前迭代，所以不会重复
            while j < len(ends) and s>=ends[j]:
                cur -= 1
                j += 1
            cur += 1    
            res = max(res, cur)
        return res