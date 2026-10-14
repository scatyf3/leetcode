class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        # merge all overlapping intervals

        # sort intervals
        # 排序是为了让「这一块合并完了」能当场下结论
        # eg: [[2,3], [4,5], [1,10]]
        # left: [1,10], [2,3], [4,5]
        # right: [[2,3], [4,5], [1,10]]，后面打乱部署
        intervals.sort()
        # print(intervals)

        # sliding windows merging
        l=0
        r=1
        merged=[]
        if len(intervals)==1:
            return intervals
        while r<len(intervals):
            if intervals[l][1]>=intervals[r][0]: # 等于也算可以merge
                # merged.append([intervals[l][0],intervals[r][1]])
                intervals[r]=[intervals[l][0],max(intervals[l][1],intervals[r][1])]
            else:
                # 相当于一直带着merge的结果往前跑，当不能merge的时候，l就是我们想要的一个最终区间
                merged.append(intervals[l])
                # r还没检查，不能merge
                # merged.append(intervals[r])
            l+=1
            r+=1
        merged.append(intervals[-1])  # 然而在最后我们需要把最后一个加进去
        return merged
