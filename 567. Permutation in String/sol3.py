class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        '''
        Input:
        - s1, s2: str, 1 <= len <= 1e4, 全小写字母
        Target: s2 里是否存在某个长度为 len(s1) 的子串, 恰好是 s1 的一个排列
        Return: 存在与否
        Output: bool

        解法: 定长滑动窗口 + 两个 26 长数组直接比较 O(26n) 时间 / O(26) 空间

        算法和 sol4.py 完全相同, 只是用 list(26) + ord(c)-97 代替 Counter。
        最快, 但多了手工下标映射; 可读性优先请看 sol4.py(慢 4.5~14 倍, 最坏仍只 19.5ms)。
        sol2.py 那版增量维护标量把 26 消成了 O(1),
        渐进更优, 但在 CPython 里反而更慢 —— 实测见文件末尾。

        为什么"更差"的复杂度跑得更快:
          win == need 是列表比较, 整个 26 次比较在 **C 层**一个循环里跑完,
          代价约等于一两条 Python 字节码。
          而增量维护标量的那 6 行, 每一行都是**解释器**在跑。
          用 C 层的 26 次换解释器的 6 次, 前者赢。
        判据: 在 Python 里, "把循环推给 C" 常常比 "降低渐进常数" 更重要。
        增量维护要到什么时候才划算 —— 窗口状态不是 26 个小整数的时候:
          比较本身是 O(k) 且 k 很大、或状态是复杂对象、或换成 C++/Java 手写比较循环。

        代码上的好处更实在: 没有 push/pop 的顺序不变式要守, 几乎写不错。
        sol.py 翻车、sol2.py 需要一大段注释解释"判断和修改的先后顺序为什么相反",
        这一版没有任何这类心智负担。
        '''
        n, m = len(s1), len(s2)
        if n > m:                          # s1 比 s2 长, 不可能塞得下
            return False

        need = [0] * 26                    # s1 的字符分布, 建好就不动
        win  = [0] * 26                    # 当前窗口的字符分布
        for c in s1:
            need[ord(c) - 97] += 1
        for i in range(n):                 # 建第一个窗口 s2[0:n]
            win[ord(s2[i]) - 97] += 1
        if win == need:
            return True

        for r in range(n, m):              # 每步: 进 s2[r], 出 s2[r-n], 比一次
            win[ord(s2[r]) - 97] += 1
            win[ord(s2[r - n]) - 97] -= 1
            if win == need:
                return True
        return False

        '''
        实测 (CPython 3.12, 每个用例跑 20 次取平均):
          写法                          s1=1e4/s2=1e4   s1=2/s2=1e4   s1=26/s2=1e4
          A 闭包 push/pop + Counter        1.92 ms        3.54 ms        3.60 ms
          B 内联标量 + list(26)            1.36 ms        1.76 ms        1.72 ms
          C 两数组比较 (本文件)            1.11 ms        1.28 ms        1.34 ms
        后两列是特意构造的对 C 最不利的场景(窗口短 -> 比较次数最多), C 仍然最快。
        A 慢在闭包调用 + nonlocal + Counter 哈希; B 去掉这些就快了一截, 但仍输给 C。

        面试怎么答: 先给这一版, 然后主动补一句"26 可以用增量维护 matched/missing
        消成 O(1), 但字符集固定 26 且常数极小, 实践中不必要" —— 说明你知道那条路,
        同时给出了不走的理由。只会写 O(26n) 和"知道 O(n) 但选择不写"是两回事。

        四个版本:
          sol.py   第一版尝试, 删键导致假阳性, 顶部有完整的错因分析
          sol2.py  增量维护标量, 渐进 O(n), 想法对但在 Python 里过度优化
          sol3.py  本文件, list(26) + ord 映射, 最快
          sol4.py  同算法换 Counter, 可读性最好 —— 首选

        Test Cases:
        ("ab",  "eidbaooo")      -> True    经典样例, "ba" 在中间
        ("ab",  "eidboaoo")      -> False   字符都有但不连续
        ("abc", "abxc")          -> False   sol.py 删键版本在这里假阳性
        ("a",   "a")             -> True    最小规模
        ("ab",  "a")             -> False   len(s1) > len(s2), 走开头的早返回
        ("adc", "dcda")          -> True    答案是末尾的 "cda"
        ("hello","ooolleoooleh") -> False   重数不匹配(o 太多), 只看字符集会误判
        '''
