class Solution:
    def longestPalindrome(self, s: str) -> str:
        '''
        Input:
        - s: str, 1 <= len(s) <= 1000
        Target: 最长回文子串
        Return: 子串本身
        Output: str

        解法: 区间 DP  O(n^2) 时间 / O(n^2) 空间
        比 sol1 差(多了 O(n^2) 空间), 但状态定义能直接迁移到 516/647/1312,
        所以值得写一遍。真正的考点是遍历顺序, 不是转移方程。
        '''
        n = len(s)
        if n == 0:
            return ""

        # f[i][j] = s[i..j] (闭区间) 是否为回文
        f = [[False] * n for _ in range(n)]
        for i in range(n):
            f[i][i] = True                      # 单字符天然回文

        bl, br = 0, 0                           # 答案区间 [bl, br], 初值 = 第一个字符
        # 关键: 必须按区间长度递增遍历!
        # f[i][j] 依赖 f[i+1][j-1] (左下方的格子), 双层正序 i,j 会读到还没算的值。
        # 等价的替代写法是 i 倒序 + j 正序。
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] != s[j]:
                    continue                    # 两端不同, f[i][j] 保持 False
                # length==2 时内部区间 [i+1, j-1] 为空, 视为成立, 不去查表(会越界/查到脏值)
                if length == 2 or f[i + 1][j - 1]:
                    f[i][j] = True
                    if j - i > br - bl:
                        bl, br = i, j
        return s[bl : br + 1]

        '''
        Dry Run: s = "cbbd", 表格只填上三角 (i<=j)
        length=2: (0,1)"cb" 端不同 F | (1,2)"bb" 端同+length2 -> T, best=(1,2)
                  (2,3)"bd" 端不同 F
        length=3: (0,2)"cbb" s[0]=c != s[2]=b -> F
                  (1,3)"bbd" s[1]=b != s[3]=d -> F
        length=4: (0,3)"cbbd" c != d -> F
        return s[1:3] = "bb"

        易错点:
        1. 忘了按 length 递增 -> 读到未初始化的 False, 会漏解 (如 "aaaa" 只报长度 2)
        2. 漏掉 length==2 的短路 -> f[i+1][j-1] 在 i+1 > j-1 时是脏值
        3. bl,br 初值写成空区间 (0,-1) -> "ac" 这类无长回文的输入会返回 ""

        Test Cases:
        "babad" -> len 3 | "cbbd" -> "bb" | "a" -> "a" | "ac" -> "a" | "aaaa" -> "aaaa"
        '''
