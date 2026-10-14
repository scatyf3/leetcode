from collections import Counter, defaultdict


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        '''
        解法2: 一张表, +1/-1 抵消  O(n) 时间 / O(k) 空间

        思路的转折点: 不要"数两遍再比对", 而是让 t **消耗** s 数出来的库存。
        s 的字符是入库(+1), t 的字符是出库(-1)。
        如果两串真是异位词, 最后每种字符的库存都归零。

        和 sol1 比, **复杂度完全一样**(都是 O(n) 时间 / O(k) 空间, k<=26 即 O(1))。
        换写法不是为了更快, 是为了:
        - 正确性面更小: 两张表时"只遍历 s_d 够不够"依赖前面那行长度剪枝;
          一张表归零没有方向性问题, 删掉剪枝也不会错(长度不同 -> 必有值非 0)
        - 套路可复用: 抵消建模在 383 赎金信 / 389 找不同 里直接能套
        - 常数略小(少一张表、少一趟遍历), 但这只是几个百分点, 不是选它的理由
        '''
        if len(s) != len(t):
            return False

        count = defaultdict(int)      # 访问缺失 key 自动得 0, 省掉 if-else
        for a, b in zip(s, t):        # 长度已相等, 可以并排走 —— 一次循环干两件事
            count[a] += 1             # s 的字符: 入库
            count[b] -= 1             # t 的字符: 出库

        # ③ 只关心值 -> 用 .values()
        return all(v == 0 for v in count.values())
        # 等价的显式写法:
        #   for v in count.values():
        #       if v != 0:
        #           return False
        #   return True

        '''
        Dry Run: s = "rat", t = "car"
          zip 配对 (r,c) (a,a) (t,r)
          (r,c): count = {r:+1, c:-1}
          (a,a): count[a] += 1 再 -= 1 -> {r:1, c:-1, a:0}    # 同字符自己抵消, 值留 0
          (t,r): count[t] = 1, count[r] = 1-1 = 0 -> {r:0, c:-1, a:0, t:1}
          values 里有非 0 -> False

        坑: 判 "所有值为 0" 不能写成 `if count:` 或 `if len(count) == 0`。
            抵消完 key 还在, 只是值变成了 0, 字典非空。
            (想让 key 消失得手动 del, 不值当)
        '''


class SolutionCounter:
    def isAnagram(self, s: str, t: str) -> bool:
        '''
        解法2b: 面试里说完思路后的"一行版" O(n)
        Counter 就是一个专门做计数的 dict 子类, 缺失 key 读出来是 0。
        Counter("aab") -> Counter({'a': 2, 'b': 1});  两个 Counter 可以直接 ==
        '''
        return Counter(s) == Counter(t)
        # 长度剪枝都不用: 长度不同 -> 计数和不同 -> 一定有某个字符次数对不上
