
from math import comb

class Solution:
    def numberOfWays(self, startPos: int, endPos: int, k: int) -> int:
        #  C(k, (k + (endPos-startPos)) / 2)
        MOD=10**9 + 7
        d = endPos - startPos
        # abs(d) > k 反例:  startPos = 1, endPos = 10, k = 2
        # (k + d) % 2 反例：startPos = endPos = 1，k = 1
        if (k + d) % 2 or abs(d) > k:
            return 0
        r = (k + d) // 2
        return comb(k, (k + d) // 2) % MOD
