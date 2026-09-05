from typing import List


class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        '''
        不是「插入一个」, 是「一段区间塌缩成一个」-> 三段式, i 不回退, O(n)
        输入已按 start 有序, 别退化成 56 (append + sort, O(n log n)) 也别上二分
        '''
        res, i, n = [], 0, len(intervals)
        s, e = newInterval                            # 先解包, 别改调用方的对象

        while i < n and intervals[i][1] < s:          # ① 左段: 完全在 new 左边
            res.append(intervals[i]); i += 1

        while i < n and intervals[i][0] <= e:         # ② 中段: 不是"完全在右" -> 重叠, 吞掉
            s = min(s, intervals[i][0])
            e = max(e, intervals[i][1])
            i += 1
        res.append([s, e])                            # 吞完才 append, 且无条件执行

        while i < n:                                  # ③ 右段: 剩下的原样抄
            res.append(intervals[i]); i += 1

        return res
