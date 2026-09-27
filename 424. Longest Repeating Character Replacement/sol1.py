# pass4 重做的版本。形状 2(外层枚举 r, 内层收缩 l) —— 和 sol2.py 同一个骨架,
# 区别只在起手式: 这版预填 Counter(s[:k]) 让 r 从 k 起跑, sol2 从 0 起跑。
#
# 这次栽的坑在收缩那两行(见行内注释): 必须先 cnt[s[l]] -= 1 再 l += 1。
# 反过来写, 离开窗口的 s[l] 永远没被减掉, 而还留在窗口里的 s[l+1] 被白扣一次,
# cnt 从此和窗口对不上。k=0 最容易暴露 —— "ABAB" k=0 会返回 2(正确是 1);
# k>=1 时因为容得下一个错账, 反而全蒙对, 所以只挂一个 case。
#
# 预填这个起手式 pass3 判过一次"不必要"(note.md「形状 1 的第一版错在哪」第 1 条):
# 内层本来就会自己扩到那儿, seed 省不掉什么; 而且它默认了 k <= len(s) ——
# s="AB" k=5 时 range(5, 2) 是空的, 一次都不进循环, 直接返回 max_len=5。
# LeetCode 约束了 k <= s.length 所以线上过得去, 但拿它当模版套别的题会栽。
# 默认写法仍然认 sol2(见 note.md 末尾的双指针决策表)。
from collections import Counter        # 本地跑要 import, LeetCode 上不写也能过


class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        if len(s)==0:
            return 0
        cnt = Counter(s[:k])
        l=0
        max_len=window_len=k
        for r in range(k,len(s)): # 枚举r，收缩l
            cnt[s[r]]+=1
            while (r-l+1)-max(cnt.values())>k: # window len-max>=k, invalid,shrink l
                cnt[s[l]]-=1
                l+=1 # 先remove cnt再挪l，否则有问题
            max_len=max(r-l+1,max_len)
        return max_len
