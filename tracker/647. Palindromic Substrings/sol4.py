class Solution:
    def countSubstrings(self, s: str) -> int:
        '''
        Input:
        - s: str, 1 <= len(s) <= 1000
        Target: 回文子串个数
        Return: int
        Output: int

        解法: Manacher  O(n) 时间 / O(n) 空间   <- 面试不要求, 收集用
        和 LC5/sol3.py 是同一份 Manacher, 只换最后的结算:
            LC5  取 p[] 的最大值
            647  求 sum((p[i] + 1) // 2)
        为什么是 (p[i]+1)//2: 插桩串上以 i 为中心、半径 <= p[i] 的回文有 p[i]+1 个
        (半径 0..p[i]), 其中恰好一半对应原串的非空回文(另一半中心落在 "#" 上且半径为偶
        的情形会退化成空串), 向上取整即 (p[i]+1)//2。
        '''
        if not s:
            return 0

        t = "#" + "#".join(s) + "#"      # "abba" -> "#a#b#b#a#", 长度恒为奇数, 奇偶中心统一
        m = len(t)
        p = [0] * m                      # p[i]: 以 t[i] 为中心的回文半径(不含中心本身)
        c = r = 0                        # c: 右边界最靠右的回文的中心; r: 它的右边界

        for i in range(m):
            if i < r:
                p[i] = min(r - i, p[2 * c - i])     # 继承镜像的半径, 但不能超出 r
            while i - p[i] - 1 >= 0 and i + p[i] + 1 < m and t[i - p[i] - 1] == t[i + p[i] + 1]:
                p[i] += 1
            if i + p[i] > r:             # r 全程只右移, 最多 m 步 -> 摊还 O(n)
                c, r = i, i + p[i]

        return sum((x + 1) // 2 for x in p)

        '''
        Dry Run: s = "aaa" -> t = "#a#a#a#" (m=7)
          p = [0, 1, 2, 3, 2, 1, 0]
          (p+1)//2 = [0, 1, 1, 2, 1, 1, 0] -> 和 = 6 ✓
          对照 sol2 的 dry run: 每个中心贡献的数一模一样, 只是这里 O(n) 算出来。

        Test Cases: 与 sol1/sol2 完全一致(已随机对拍 3000 组)
        '''
