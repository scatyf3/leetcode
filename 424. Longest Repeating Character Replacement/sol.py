# 第一版尝试, 没通过 —— 直接 IndexError, 不是 WA。四个问题:
#   1. while 里先 r+=1 再取 s[r], 而 r<n 验的是自增前的 r -> s[n] 越界(崩的直接原因)
#   2. max_len 用了 l-r+1, 方向反了, 应该 r-l+1 (valid 里写的却是对的, 自相矛盾)
#   3. 内外两层循环都在 cnt[..] += 1, 同一个字符被数两遍, 窗口状态从此不对
#   4. while 条件没取反: 骨架 A 是 "while not valid: 收缩", 不是 "while valid: 扩"
#      根子上是 l/r 角色对调了 —— 外层该是 r(纳入), 内层推进 l(移出)
# 修正版见 sol2.py。
from collections import Counter        # 本地跑要 import, LeetCode 上不写也能过

class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        '''
        s str
        k: k times change
        return longest substr with same char
        '''
        l = r = 0
        cnt = Counter()
        n = len(s)
        max_len = 0
        for l in range(n):
            cnt[s[l]]+=1
            while self.valid(cnt,l,r,k) and r<n:
                r+=1
                cnt[s[r]]+=1
            max_len = max(max_len,l-r+1)
            cnt[s[l]]-=1
        return max_len

    def valid(self,cnt,l,r,k):
        max_cnt = max(cnt.values())
        return r-l+1-max_cnt<=k
