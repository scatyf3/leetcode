from collections import Counter        # 本地跑要 import, LeetCode 上不写也能过

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        '''
        Input:
        - s1, s2: str, 1 <= len <= 1e4, 全小写字母
        Target: s2 里是否存在某个长度为 len(s1) 的子串, 恰好是 s1 的一个排列
        Return: 存在与否
        Output: bool

        解法: 定长滑动窗口 + 增量维护一个整数 O(n) 时间 / O(26) 空间

        观察一: 窗口是**定长**的。
          s1 的排列长度恒为 n = len(s1), 所以这题不是"枚举右、invalid 时收缩左"
          那种变长窗口 —— 左边界恒等于 r - n, 连 l 这个变量都不用存。
          sol.py 的注释里把两种骨架混着写了, 这是最初的思路混乱点。

        观察二: 判定可以增量化 —— 但这题**不该这么做**, 见下面的注意。
          naive 是每次比较两张 26 长的计数表, O(26n)。每次滑动只有 2 个格子变了,
          却扫 26 个, 看起来是白做功。改成增量维护一个标量 missing 就是每步 O(1),
          判定退化成一次整数比较。
          通用套路: 窗口里凡是要做全量扫描, 先问一句"这个量能不能增量更新"。

        注意: 这个优化在 CPython 里是**负收益**, 实测本版比 O(26n) 的 sol3.py 慢。
          原因: win == need 的 26 次比较在 C 层一个循环里跑完, 约等于一两条字节码;
          而这里维护标量的每一行都是解释器在跑。用 C 层的 26 次换解释器的 6 次, 前者赢。
          实测数据见 sol3.py 末尾。**实战写 sol3.py。**
          本文件保留, 是因为增量维护的思路本身通用 —— 当窗口状态不是 26 个小整数
          (比较本身 O(k) 且 k 大、状态是复杂对象、或换成 C++/Java 手写比较循环)时,
          它才真正划算。这题不属于那种情况。
          (再往上没有了, O(n) 是下界 —— s2 总得读一遍。有人想把 26 个计数压成一个
           整数做滚动哈希, 但计数不是集合, 位运算表达不了重数, 随机哈希又要处理碰撞,
           收益为负。)

        数据结构上要分清三样东西, 混在一起就会写错(sol.py 就是混了):
          1. 恒定事实   s1 需要哪些字符、各几个   -> need 的**键集合**, 全程不删
          2. 随窗口变的 每个字符还差几个         -> need 的**值**, 允许为负(负 = 超量)
          3. 摘要状态   总共还差几个             -> missing, 一个**独立的 int**
        '''
        n, m = len(s1), len(s2)
        if n > m:                       # s1 比 s2 长, 不可能塞得下
            return False

        need = Counter(s1)              # 键集合全程不动; 值可以变负, 表示窗口里超量
        missing = n                     # 还差几个字符才凑齐 s1

        def push(c):                    # 字符进窗口 -> 需求减
            nonlocal missing
            if need[c] > 0:             # 先判断: >0 说明这个字符还欠着, 这次进的有用
                missing -= 1
            need[c] -= 1                # 后修改; s1 里没有的字符会变负, 正确记下超量

        def pop(c):                     # 字符出窗口 -> 需求加
            nonlocal missing
            need[c] += 1                # 先修改
            if need[c] > 0:             # 后判断: 变成 >0 说明重新欠账了
                missing += 1

        # push/pop 里"判断"和"修改"的先后顺序必须相反。两边判的是同一件事 ——
        # "c 处于欠账状态" —— 而这个状态由**计数为正的那一侧**决定:
        # 进的时候是修改前为正, 出的时候是修改后为正。顺序写反会漏加漏减。

        for i in range(n):              # 建第一个窗口 s2[0:n]
            push(s2[i])
        if missing == 0:
            return True

        for r in range(n, m):           # 每步三件事: 进 s2[r], 出 s2[r-n], 查 missing
            push(s2[r])
            pop(s2[r - n])
            if missing == 0:
                return True
        return False

        '''
        为什么 missing == 0 就够了, 不用另外检查"有没有超量"?
          窗口长度恒为 n, s1 长度也是 n, 所以 sum(need.values()) 恒等于 0(总数守恒)。
          missing == 0 意味着每个 need[c] <= 0; 一堆非正数加起来是 0, 只能全是 0。
          => 每个字符数量精确相等 = 排列。超量的情况被守恒律自动排除了。

        Dry Run: s1 = "abc", s2 = "abxc"   (就是 sol.py 那版答错的反例, 正确答案 False)
          init  need={a:1,b:1,c:1}  missing=3
          push a   need[a]=1>0  -> missing=2, need[a]=0
          push b                -> missing=1, need[b]=0
          push x   need[x]=0 不>0 -> missing 不变=1, need[x]=-1   (超量, 记下)
          窗口 "abx", missing=1 != 0
          r=3: push c  need[c]=1>0 -> missing=0, need[c]=0
               pop  a  need[a]=0+1=1>0 -> missing=1   <-- 关键: 需求被**恢复**了
               窗口 "bxc", missing=1 != 0
          return False  ✓
        对比 sol.py: 那版在 push c 之后 need 已空, 直接返回 True(错)。
        差别就在 pop 这一步能不能把 a 的需求还回来 —— 删了键就还不回来。

        Test Cases:
        ("ab",  "eidbaooo")  -> True    经典样例, "ba" 在中间
        ("ab",  "eidboaoo")  -> False   字符都有但不连续
        ("abc", "abxc")      -> False   删键版本在这里假阳性, 见上面 Dry Run
        ("a",   "a")         -> True    最小规模
        ("ab",  "a")         -> False   len(s1) > len(s2), 走开头的早返回
        ("adc", "dcda")      -> True    答案是末尾的 "cda"
        ("hello","ooolleoooleh") -> False  重数不匹配(o 太多), 光看字符集会误判
        '''
