from collections import Counter        # 本地跑要 import, LeetCode 上不写也能过

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        '''
        Input:
        - s: str, 1 <= len(s) <= 1e5
        - t: str, 1 <= len(t) <= 1e5, 大小写字母(注意不只是小写, 所以不能用 list(26))
        Target: s 中**最短**的子串, 使其包含 t 的所有字符(含重数)
        Return: 该子串; 不存在返回 ""
        Output: str

        解法: 变长滑动窗口(枚举右, valid 时收缩左) O(len(s)) 时间 / O(字符集) 空间

        和 567 的区别 —— 这是这题唯一要想清楚的事:
          567  窗口**定长**, 判定是**相等**(窗口 == s1 的字符分布, 一个不多一个不少)
          76   窗口**变长**, 判定是**覆盖**(窗口 ⊇ t, **允许有多余字符**)
          所以 567 能用 win == need, 这题不能 —— 用 == 会漏掉所有带多余字符的合法窗口,
          而合法窗口几乎都带多余字符。
          有意思的是: "枚举右, invalid 收缩左" 这个骨架套在 567 上是错的(那题定长),
          套在这题上才对。567 的 sol2.py 里那个 missing 标量在那边是过度优化,
          在这边是**必需**的。

        收缩的时机(最容易想反的地方):
          不是"因为多了某个字符所以收缩"。
          是"**窗口一旦 valid, 就一直往里收, 收到刚好不 valid 为止, 路上每步结算**"。
          收缩不为恢复合法(它本来就合法), 是为了找出当前右端点下**最短**的左端点。
          判据从头到尾只有一个: valid / 不 valid。

        为什么不用 Counter 的 <= 或 > 做覆盖判定:
          Python 3.10+ 的 Counter 比较是**偏序, 不是全序**, 不满足三分律:
            need = Counter('ABC'), win = Counter('AD')
            need > win   -> False   (need 里没有 D)
            need <= win  -> False   (win 里没有 B, C)
          "有多余字符但又缺东西"是窗口最常见的状态, 此时两个判断全 False,
          写成 if/elif 会两个分支都不进 -> r 不推进 -> **死循环**。
          missing 是个 int, 全序、O(1)、不会误判。
        '''
        lens, lent = len(s), len(t)
        if lent > lens:
            return ""

        need = Counter(t)          # 还差几个某字符; 允许变负, 负 = 窗口里多了几个
        missing = lent             # 总共还差几个字符才覆盖 t; == 0 即 valid

        best_len = lens + 1        # 哨兵: 比任何合法窗口都大, 用来判"从没找到过"
        best_l = 0
        l = 0

        for r in range(lens):
            c = s[r]               # 扩右: 纳入 s[r]
            if need[c] > 0:        # 先判断: >0 说明这个字符还欠着, 这次纳入有用
                missing -= 1
            need[c] -= 1           # 后修改; t 里没有的字符会变负, 正确记下"多余"

            while missing == 0:    # valid 了就一直收, 收到崩为止; 每步先结算
                if r - l + 1 < best_len:
                    best_len = r - l + 1
                    best_l = l     # 只存下标, 不存切片 —— 存切片是 O(n) 拷贝
                c = s[l]           # 收左: 移出 s[l]
                need[c] += 1       # 先修改
                if need[c] > 0:    # 后判断: 变成 >0 说明重新欠账, 窗口不再 valid
                    missing += 1
                l += 1

        return "" if best_len > lens else s[best_l:best_l + best_len]

        '''
        push/pop 的"判断与修改顺序必须相反", 和 567 的 sol2.py 是同一回事:
        两边判的是同一件事 —— "c 还欠着" —— 而它由**计数为正的那一侧**决定:
        纳入时是修改**前**为正, 移出时是修改**后**为正。顺序写反会漏加漏减。

        need[c] 变负在这题意义更直观: 负多少 = 窗口里多了几个, 正是收缩时可以白白
        消耗掉的余量。移出一个多余字符时 need[c] 从 -1 变 0, 不 >0, missing 不动,
        窗口依然 valid, 于是 while 继续收 —— 这正是"把多余的挤出去"的过程。

        Dry Run: s = "ADOBECODEBANC", t = "ABC"   (下面是程序实际跑出来的 trace)
          下标 0:A 1:D 2:O 3:B 4:E 5:C 6:O 7:D 8:E 9:B 10:A 11:N 12:C

          r=0..4   纳入 A D O B E     missing 3 -> 2(A) -> 1(B), 还差 C
          r=5      纳入 C  missing=0  窗口 s[0:6]="ADOBEC"  valid
                   结算 len=6  ** best=6 **
                   移出 A -> need[A] 0->1 >0 -> missing=1, l=1   窗口崩了, 退出收缩

          r=6..9   纳入 O D E B       全是多余的(need 更负), missing 保持 1
          r=10     纳入 A  missing=0  窗口 s[1:11]="DOBECODEBA"  valid
                   收缩连收 5 步, 每步都结算, 但都不如 best=6:
                     移 D -> missing=0 (D 是多余的)   s[2:11] len=9
                     移 O -> missing=0                s[3:11] len=8
                     移 B -> missing=0  <-- 注意! 下标 9 还有一个 B, 所以移掉不崩
                     移 E -> missing=0                s[5:11] len=6
                     移 C -> need[C] 0->1 >0 -> missing=1, l=6   崩, 退出

          r=11     纳入 N  多余
          r=12     纳入 C  missing=0  窗口 s[6:13]="ODEBANC"  valid
                   收缩: 移 O(多余) -> s[7:13] len=6
                         移 D(多余) -> s[8:13]="EBANC" len=5  ** best=5 **
                         移 E(多余) -> s[9:13]="BANC"  len=4  ** best=4 **
                         移 B -> missing=1, l=10  崩, 退出
          return s[9:13] = "BANC"   ✓

        两个值得看的点:
          1. r=10 那次收缩里移出 B 竟然没崩 —— 因为下标 9 还有一个 B 兜着,
             need[B] 当时是 -1, +1 后是 0, 不 >0。这就是"多余量被挤出去"的过程。
          2. 最终答案 "BANC" 是在**收缩循环内部**结算出来的, 而且是连着两次更新
             (5 再 4)。如果把结算写在收缩循环**之后**, 这两个都会错过 —— 这就是
             上面那个自查题的答案。

        Test Cases:
        ("ADOBECODEBANC", "ABC")  -> "BANC"   经典样例, 答案在末尾不在开头
        ("a", "a")                -> "a"      最小规模
        ("a", "aa")               -> ""       重数不够, 光看字符集会误判
        ("ab", "b")               -> "b"      答案不含左端
        ("bba", "ab")             -> "ba"
        ("a", "b")                -> ""       无解
        ("ABC", "ABCD")           -> ""       len(t) > len(s), 走开头的早返回
        ("aa", "aa")              -> "aa"     整串就是答案
        '''
