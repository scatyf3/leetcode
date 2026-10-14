class Solution:
    def longestPalindrome(self, s: str) -> str:
        '''
        Input:
        - s: str, 1 <= len(s) <= 1000
        Target: 最长回文子串
        Return: 子串本身
        Output: str

        解法: Manacher  O(n) 时间 / O(n) 空间
        面试不要求, 收集用。两个核心 trick:
        1. 插桩 "#" 把偶数长度回文也变成奇数 -> 奇偶两种中心统一成一种
        2. 用当前最靠右回文的镜像, 继承一个"免费"的初始半径 -> 总扩展次数摊还 O(n)
        '''
        if not s:
            return ""

        # "abba" -> "#a#b#b#a#"; 插桩后长度恒为奇数 2n+1, 每个回文中心都落在某个字符上
        t = "#" + "#".join(s) + "#"
        m = len(t)
        p = [0] * m          # p[i]: 以 t[i] 为中心的回文半径(不含中心本身)
        c = r = 0            # c: 当前右边界最靠右的那个回文的中心; r: 它的右边界

        for i in range(m):
            if i < r:
                # i 关于 c 的镜像是 2c-i。镜像处的半径可以直接继承,
                # 但不能超出 r (超出部分没被验证过, 得老实扩)
                p[i] = min(r - i, p[2 * c - i])
            # 只做"额外"的扩展: 继承来的部分不重复比较, 这是 O(n) 的来源
            while i - p[i] - 1 >= 0 and i + p[i] + 1 < m and t[i - p[i] - 1] == t[i + p[i] + 1]:
                p[i] += 1
            if i + p[i] > r:                 # r 全程只右移, 最多 m 步 -> 摊还 O(n)
                c, r = i, i + p[i]

        k = max(range(m), key=lambda i: p[i])
        # 插桩串上的半径 p[k] 恰好等于原串上的回文长度; 起点做个坐标换算
        start = (k - p[k]) // 2
        return s[start : start + p[k]]

        '''
        为什么 p[k] 就是原串长度:
          t 中一个半径为 p 的回文, 覆盖 2p+1 个字符, 其中 p 个是原字符、p+1 个是 "#"
          (插桩保证两者交替, 且回文两端一定是 "#") -> 原串长度 = p

        和 LC3 的联系: 这里 r 单调右移, 和 LC3 里左边界 l 单调不减是同一个摊还论证。
        参见 notes/sliding-window-template.md 和 3. 那题的 note。

        Dry Run: s = "abba" -> t = "#a#b#b#a#" (m=9)
          i=4 (中间那个 '#'), 向两边扩: b==b -> #==# -> a==a -> #==# -> 越界停, p[4]=4
          k=4, start=(4-4)//2=0, 返回 s[0:4] = "abba"

        Test Cases: 与 sol1 完全一致(已随机对拍 4000 组)
        '''
