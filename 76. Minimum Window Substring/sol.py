from collections import Counter        # 本地跑要 import, LeetCode 上不写也能过

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        lens, lent = len(s), len(t)
        if lent > lens:
            return ""

        need = Counter(t)          # 还差几个某字符; 允许变负, 负 = 窗口里多了几个
        missing = lent             # 总共还差几个字符才覆盖 t; == 0 即 valid，维护一个标量免得每次都判counter


        best_len = lens + 1        # 哨兵: 比任何合法窗口都大, 用来判"从没找到过"
        best_l = 0
        l = 0

        for r in range(lens): # 枚举r，扩充滑动窗口
            c = s[r]               # 扩右: 纳入 s[r]
            if need[c] > 0:        # 如果当前的字符在need里，扣missing
                missing -= 1       # 为啥 missing -= 1  套if里，need[c] -= 1 则不然
            need[c] -= 1           

            while missing == 0:    # valid 了就一直收左边界
                if r - l + 1 < best_len: # change best len
                    best_len = r - l + 1
                    best_l = l     # 只存下标, 不存切片 —— 存切片是 O(n) 拷贝
                c = s[l]           # 收左: 移出 s[l]
                need[c] += 1       # 先修改
                if need[c] > 0:    # 后判断: 变成 >0 说明重新欠账, 窗口不再 valid
                    missing += 1
                l += 1

        return "" if best_len > lens else s[best_l:best_l + best_len]
