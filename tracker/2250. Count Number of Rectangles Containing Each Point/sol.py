from bisect import bisect_left                       # left 还是 right？


class Solution:
    def countRectangles(self, rectangles: list[list[int]], points: list[list[int]]) -> list[int]:
        # [0,100], include 100
        MAXH = 100
        buckets = [[] for _ in range(MAXH+1)]      # 下标要能取到 MAXH
        for l, h in rectangles:
            buckets[h].append(l)      # 按哪一维分桶？桶里存哪一维？
        for b in buckets:          # 说起来这个b是copy还是reference，看起来是copy啊
            b=b.sort()                                 # 二分之前要做什么？

        ans = []
        for x, y in points:
            cnt = 0
            for h in range(y,MAXH+1):     # 哪些桶的 h 满足条件？ 在h之内的
                b = buckets[h]
                cnt += len(buckets[h]) - bisect_left(b,x)    # 桶里 l >= x 的个数
            ans.append(cnt)
        return ans
