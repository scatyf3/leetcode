class Solution:
    def countSubstrings(self, s: str) -> int:
        '''
        Input:
        - s: str, 1 <= len(s) <= 1000, 仅小写英文字母
        Target: 统计 s 中回文子串的**个数**(按出现位置算, 内容相同但位置不同算两个)
        Return: int
        Output: int

        解法: 中心扩展 O(n^2) 时间 / O(1) 额外空间
        和 LC5 是同一份骨架, 只换了"结算方式":
            LC5  取最长 -> 退出后一次性算区间
            647  数个数 -> 每扩成功一次就 cnt += 1
        为什么每次成功 = 一个新回文: 中心固定时, 半径每 +1 就得到一个更长的回文串,
        且它和之前数过的中心/半径组合两两不同 -> 不重不漏(见 note.md 的双射论证)。
        '''
        n = len(s)

        def expand(l: int, r: int) -> int:
            # 从中心 [l, r] 向两边扩, 返回以这个中心为轴的回文子串个数
            # 偶中心失配(s[l] != s[r])时首轮就退出, 自然返回 0, 不用特判
            cnt = 0
            while l >= 0 and r < n and s[l] == s[r]:
                cnt += 1          # 当前的 [l, r] 就是一个回文, 先记账再挪指针
                l -= 1
                r += 1
            return cnt

        # 2n-1 个中心: n 个奇中心(轴是字符) + n-1 个偶中心(轴是字符之间的缝)
        return sum(expand(i, i) + expand(i, i + 1) for i in range(n))

        '''
        Dry Run: s = "aaa"  (答案 6: "a"x3, "aa"x2, "aaa"x1)
        i=0 奇 expand(0,0): [0,0]"a" +1 -> l=-1 越界退出          -> 1
            偶 expand(0,1): [0,1]"aa" +1 -> [-1,2] 越界退出       -> 1
        i=1 奇 expand(1,1): [1,1]"a" +1 -> [0,2]"aaa" +1 -> 越界  -> 2
            偶 expand(1,2): [1,2]"aa" +1 -> [0,3] r 越界退出      -> 1
        i=2 奇 expand(2,2): [2,2]"a" +1 -> r=3 越界               -> 1
            偶 expand(2,3): r=3 越界, 首轮就退出                  -> 0   <- 末尾偶中心自动退化
        total = 1+1+2+1+1+0 = 6

        Test Cases:
        "abc"   -> 3    无重复, 只有单字符
        "aaa"   -> 6
        "a"     -> 1    单字符
        "aaaa"  -> 10   = C(4+1,2), 全同字符时等于 n(n+1)/2
        "abba"  -> 6    "a","b","b","a","bb","abba"  <- 漏偶中心的话会得 4
        ""      -> 0    题目保证非空, 但代码天然处理
        '''
