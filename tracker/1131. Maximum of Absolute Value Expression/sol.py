class Solution:
    def maxAbsValExpr(self, arr1: list[int], arr2: list[int]) -> int:
        res = 0
        for s1, s2 in [(1,1),(-1,1),(1,-1),(-1,-1)]:  # 枚举哪些符号组合？
            mn = float("+inf")                            # 「左边最小值」的初值
            for k in range(len(arr1)):
                v = s1 * arr1[k] + s2 * arr2[k] + k   # 当前位置 k，扮演 i
                res = max(res, v - mn)                # mn 是某个更早位置的 v，扮演 j
                mn =  min(mn,v)                       # 把 k 加入「左边」
        return res

