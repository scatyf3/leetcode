class Solution:
    def longestPalindrome(self, s: str) -> str:
        '''
        Input:
        - s: str, 1 <= len(s) <= 1000, 仅含数字和英文字母
        Target: 找出 s 中最长的回文子串
        Return: 该子串本身(不是长度); 多解时返回任意一个
        Output: str

        解法: 中心扩展 O(n^2) 时间 / O(1) 额外空间  <- 面试标准答案
        为什么不能用滑窗: 回文的合法性不向下封闭("aba" 是回文, 子串 "ab" 不是),
        所以左边界不单调, 窗口爬不动。详见 note.md。
        '''
        n = len(s)

        def expand(l: int, r: int) -> str:
            # 从中心 [l, r] 向两边扩, 返回能扩到的最长回文子串
            # 偶中心失配(s[l] != s[r])时首轮就退出, 自然返回 "", 不用特判
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            # 退出时 l/r 已经站在第一个"不合法"的位置上(while 是先测后走),
            # 要的是最后一个合法区间 [l+1, r-1]; 切片右端是开区间, 正好省掉那个 -1
            return s[l + 1 : r]

        best = ""
        for i in range(n):
            best = max(best,
                       expand(i, i),      # 奇中心: 轴是 s[i] 一个字符    -> 奇数长度
                       expand(i, i + 1),  # 偶中心: 轴是 s[i]|s[i+1] 的缝 -> 偶数长度
                       key=len)
        return best

        '''
        Dry Run: s = "cbbd"
        i=0 奇 expand(0,0): l=-1 越界退出 -> s[0:1]="c"
            偶 expand(0,1): s[0]=c != s[1]=b 首轮失配 -> s[1:1]=""
        i=1 奇 expand(1,1): s[0]=c != s[2]=b 退出 -> s[1:2]="b"
            偶 expand(1,2): b==b 匹配 -> (0,3): c != d 退出 -> s[1:3]="bb"  <- best
        i=2 奇 -> "b";  偶 expand(2,3): b != d -> ""
        i=3 奇 -> "d";  偶 expand(3,4): r=4 越界 -> ""   <- 末尾偶中心自动退化, 无需 if
        return "bb"

        Test Cases:
        "babad" -> "bab" (或 "aba", 都算对)
        "cbbd"  -> "bb"       偶中心
        "a"     -> "a"        单字符
        "ac"    -> "a"        无 >1 的回文, 靠 best="" 的 max 兜底
        "aaaa"  -> "aaaa"     全同字符, 一路扩到边界
        "forgeeksskeegfor" -> "geeksskeeg"
        '''
