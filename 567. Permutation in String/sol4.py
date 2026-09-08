from collections import Counter        # 本地跑要 import, LeetCode 上不写也能过

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        '''
        Input:
        - s1, s2: str, 1 <= len <= 1e4, 全小写字母
        Target: s2 里是否存在某个长度为 len(s1) 的子串, 恰好是 s1 的一个排列
        Return: 存在与否
        Output: bool

        解法: 定长滑动窗口 + 两个 Counter 直接比较 O(26n) 时间 / O(26) 空间

        **首选这一版。** 和 sol3.py 是同一个算法, 只是把 list(26) + ord(c)-97
        换成 Counter, 省掉字符到下标的手工映射。慢 4.5~14 倍但最坏 19.5ms, 见末尾。

        核心观察: 窗口是**定长**的。
          s1 的排列长度恒为 n = len(s1), 所以这题不是"枚举右、invalid 时收缩左"
          那种变长窗口 —— 左边界恒等于 r - n, 连 l 变量都不用存。
          sol.py 的注释里把两种骨架混着写了, 这是最初的思路混乱点。
        '''
        n, m = len(s1), len(s2)
        if n > m:                      # s1 比 s2 长, 不可能塞得下
            return False

        need = Counter(s1)             # s1 的字符分布, 建好就不动
        win  = Counter(s2[:n])         # 当前窗口的字符分布
        if win == need:
            return True

        for r in range(n, m):          # 每步: 进 s2[r], 出 s2[r-n], 比一次
            win[s2[r]] += 1
            win[s2[r - n]] -= 1
            if win == need:
                return True
        return False

        '''
        两个 Counter 的坑, 这里都不用管, 但要知道为什么:

        1. 计数减到 0 的键**不会自动删除**, 会以 {'a': 0} 的形式留在字典里。
           所有"原地修改"(win[c] -= 1, .subtract()) 都保留 0 甚至负数;
           只有"生成新 Counter"的二元运算(+ - & |)和一元 +c/-c 会剥掉非正数。
           另外 win[c] -= 1 对不存在的键会**顺手插入** -1(复合赋值是先读后写),
           而纯读取 win[c] 返回 0 但不插入。
        2. 但 Python **3.10+** 的 Counter.__eq__ 已改成多重集语义, 会忽略 0 计数:
              Counter({'a': 0}) == Counter()   ->   True
           所以这里直接 win == need 是**对的**, 不用手动 del。
           3.9 及更早继承 dict.__eq__, 上面那句是 False, 那时才需要清理。
           LeetCode 的 Python3 是 3.11+, 放心用。

        为什么这里的"零值残留"无害, 而 sol.py 的删键会翻车:
          win 表示"窗口里各字符有几个", 缺席 == 0 是**忠实**的表示, 删不删都不丢信息,
          而且 win[c] += 1 能把它正确地复活回来。
          sol.py 删的是 need 的键 —— 那编码的是"s1 需要什么"这个**恒定事实**,
          删掉之后配合 `if c in need` 守卫, 字符移出窗口时需求就再也恢复不了了。
          差别不在"删不删", 在**删掉的东西是不是可恢复的**。

        实测 (CPython 3.12, len(s2)=1e4, 构造成全程无命中走满整个 s2, 每例 20 次):
          n=len(s1)      Counter    list(26)   倍数
          2              19.52ms      1.40ms   13.9x
          10             12.84ms      1.98ms    6.5x
          26             10.59ms      1.48ms    7.2x
          100            10.13ms      1.37ms    7.4x
          1000            8.71ms      1.28ms    6.8x
          5000            5.19ms      1.14ms    4.5x
        Counter 的 == 要走 dict 哈希、逐键 all(...) 生成器; list 的 == 是 C 层
        一个循环扫 26 个小整数。差距全在这里。n 小时窗口比较次数最多, 差距最大。
        最坏 19.5ms 距离 LeetCode 的秒级限时还远, 所以这点常数换可读性是划算的。

        四个版本:
          sol.py   第一版尝试, 删 need 的键导致假阳性, 顶部有完整错因分析
          sol2.py  增量维护标量 missing, 渐进 O(n), 想法通用但在 Python 里是负收益
          sol3.py  list(26) + ord(c)-97, 最快, 但有手工下标映射
          sol4.py  本文件, 同算法换 Counter, 可读性最好 —— 首选

        Test Cases:
        ("ab",  "eidbaooo")      -> True    经典样例, "ba" 在中间
        ("ab",  "eidboaoo")      -> False   字符都有但不连续
        ("abc", "abxc")          -> False   sol.py 删键版本在这里假阳性
        ("a",   "a")             -> True    最小规模
        ("ab",  "a")             -> False   len(s1) > len(s2), 走开头的早返回
        ("adc", "dcda")          -> True    答案是末尾的 "cda"
        ("hello","ooolleoooleh") -> False   重数不匹配(o 太多), 只看字符集会误判
        '''
