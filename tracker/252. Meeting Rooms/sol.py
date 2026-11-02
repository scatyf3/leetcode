class Solution:
    def canAttendMeetings(self, intervals: list[list[int]]) -> bool:
        intervals.sort()

        last=[]

        for interval in intervals:
            if last and last[1]>interval[0]:
                return False
            else:
                last=interval
        return True
