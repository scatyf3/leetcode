class Solution:
    def minMeetingRooms(self, intervals: list[list[int]]) -> int:
        # given list of interval, detact max overlap
        # define point
        ckpt=set()
        start_interval=Counter()
        end_interval=Counter()
        for interval in intervals:
            ckpt.add(interval[0])
            ckpt.add(interval[1])
            start_interval[interval[0]]+=1
            end_interval[interval[1]]+=1
        ckpt_lst = list(ckpt)
        mx=0
        cur=0
        ckpt_lst.sort()
        # print(ckpt_lst)
        for point in ckpt_lst:
            if point in start_interval:
                cur+=start_interval[point]
            if point in end_interval:
                cur-=end_interval[point]
            mx=max(cur,mx)
        return mx
            