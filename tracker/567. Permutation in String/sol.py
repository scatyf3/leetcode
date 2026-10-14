from collections import Counter        # 本地跑要 import, LeetCode 上不写也能过


class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        '''
        Input:
        - s1, s2: str, 1 <= len <= 1e4, 全小写字母
        Target: s2 里是否存在某个长度为 len(s1) 的子串, 恰好是 s1 的一个排列
        Return: 存在与否
        Output: bool

        解法: 定长滑动窗口 + 两个 Counter 直接比较   O(26n) 时间 / O(26) 空间

        核心观察: 窗口是**定长**的。
          s1 的排列长度恒为 n = len(s1), 所以这题不是「枚举 r, invalid 时收缩 l」
          那种变长窗口 —— 左边界恒等于 r - n, 连 l 这个变量都不用存。
          每步只做三件事: 进 s2[r], 出 s2[r-n], 比一次。
          判据见 notes/sliding-window-template.md: 窗口长度被题面钉死 -> 定长。

        为什么敢用 O(26n) 的全量比较而不做增量维护, 见 note.md「三条砍掉的路」。
        '''
        n, m = len(s1), len(s2)
        if n > m:                      # s1 比 s2 长, 不可能塞得下
            return False

        need = Counter(s1)             # s1 的字符分布, 建好就不动
        win  = Counter(s2[:n])         # 当前窗口的字符分布
        if win == need:
            return True

        for r in range(n, m):
            win[s2[r]] += 1            # 进
            win[s2[r - n]] -= 1        # 出
            if win == need:
                return True
        return False

        '''
        唯一要知道的语义坑: Counter 计数减到 0 的键**不会**自动删除, 会以 {'a': 0}
        的形式留在字典里。但 Python **3.10+** 的 Counter.__eq__ 改成了多重集语义,
        会忽略 0 计数:
            Counter({'a': 0}) == Counter()   ->   True
        所以这里直接 win == need 是对的, 不用手动 del。
        (3.9 及更早继承 dict.__eq__, 上面那句是 False, 那时才需要清理; LeetCode 是 3.11+。)

        另一个相关的坑: win[c] -= 1 对不存在的键会**顺手插入** -1(复合赋值先读后写),
        而纯读取 win[c] 返回 0 但不插入。这里两边都无害 —— win 记的是「窗口里有几个」,
        缺席 == 0 是忠实表示, 删不删都不丢信息, += 1 也能把它正确复活。

        Test Cases:
        ("ab",   "eidbaooo")     -> True    经典样例, "ba" 在中间
        ("ab",   "eidboaoo")     -> False   字符都有但不连续
        ("abc",  "abxc")         -> False   「删键」写法在这里假阳性, 见 note.md
        ("ab",   "axxxb")        -> False   「不收缩左边界」写法在这里假阳性
        ("ab",   "aab")          -> True    「不收缩左边界」写法在这里假阴性
        ("a",    "a")            -> True    最小规模
        ("ab",   "a")            -> False   len(s1) > len(s2), 走开头的早返回
        ("adc",  "dcda")         -> True    答案是末尾的 "cda"
        ("hello","ooolleoooleh") -> False   重数不匹配(o 太多), 只看字符集会误判
        '''
