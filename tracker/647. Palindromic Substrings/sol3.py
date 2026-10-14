class Solution:
    def countSubstrings(self, s: str) -> int:
        '''
        Input:
        - s: str, 1 <= len(s) <= 1000
        Target: 回文子串个数
        Return: int
        Output: int

        解法: 区间 DP  O(n^2) 时间 / O(n^2) 空间
        比 sol2 的中心扩展差(多了 O(n^2) 空间), 但状态 f[i][j] = "s[i..j] 是否回文"
        和 LC5/sol2.py 一字不差 —— 只是把"记录最长区间"换成"计数 +1"。
        写它的价值: 这套状态和"按区间长度递增"的遍历顺序能迁到 516/1312/312。
        '''
        n = len(s)
        f = [[False] * n for _ in range(n)]      # f[i][j]: s[i..j] 闭区间是否回文

        cnt = n                                   # 每个单字符天然是回文, 先算 n 个
        for i in range(n):
            f[i][i] = True

        # 关键: 必须按区间长度递增遍历!
        # f[i][j] 依赖 f[i+1][j-1] (左下方的格子), 双层正序 i,j 会读到还没算的值。
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] != s[j]:
                    continue                      # 两端不同, f[i][j] 保持 False
                # length==2 时内部区间 [i+1, j-1] 为空, 视为成立, 不去查表(会查到脏值)
                if length == 2 or f[i + 1][j - 1]:
                    f[i][j] = True
                    cnt += 1
        return cnt

        '''
        Dry Run: s = "aaa"
        init: f[0][0]=f[1][1]=f[2][2]=True, cnt=3
        length=2: (0,1) a==a 且 length==2 -> T, cnt=4
                  (1,2) a==a              -> T, cnt=5
        length=3: (0,2) a==a 且 f[1][1]=T -> T, cnt=6
        return 6

        易错点(和 LC5/sol2 同源):
        1. 忘了按 length 递增 -> 读到未初始化的 False, 少数长回文
        2. 漏掉 length==2 的短路 -> f[i+1][j-1] 在 i+1 > j-1 时是脏值
        3. cnt 初值忘了 n -> 漏掉全部单字符

        Test Cases: 与 sol1/sol2 完全一致(已随机对拍)
        '''
