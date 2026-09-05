from typing import List


class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        '''
        naive: 不断两两比较合并直到没有 overlap, O(n^2) 起

        按 start 排序后, 新区间只可能和「最后一个已合并区间」重叠 -> 内层循环消掉, O(n)
        证明和排序键的推法见 paradigms/intervals.md §1
        '''
        intervals.sort(key=lambda x: x[0])        # 按 start 排
        res = []
        for s, e in intervals:
            if res and s <= res[-1][1]:           # 重叠 (= 因为本题端点相碰算重叠)
                res[-1][1] = max(res[-1][1], e)   # 往外推; max 是为了 [[1,10],[2,3]] 这种包含关系
            else:
                res.append([s, e])                # 不重叠, 开新的 (必须 append 新 list)
        return res
