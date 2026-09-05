# 滑动窗口, 骨架 A(求最长合法窗口)。第一版为什么不对见 sol.py 顶上的注释。
# 不变式: 结算的那一刻, 窗口 [l, r] 一定合法。
# 合法 = 把窗口里非众数的字符全换掉, 花费不超过 k, 即 (窗口长 - 最大频次) <= k。
from collections import Counter

class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        cnt = Counter()
        l = best = 0
        for r, x in enumerate(s):
            cnt[x] += 1                                   # ① 纳入 r, 无条件
            while (r - l + 1) - max(cnt.values()) > k:     # ② 破坏不变式就收缩, 单向
                cnt[s[l]] -= 1
                l += 1
            best = max(best, r - l + 1)                    # ③ 此刻必合法, 直接结算
        return best
