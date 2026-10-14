class Solution:
    def longestDiverseString(self, a: int, b: int, c: int) -> str:
        cnt = [[a, 'a'], [b, 'b'], [c, 'c']]
        res = []
        while True:
            cnt.sort(reverse=True)                 # cnt[0] 最多，cnt[1] 第二多
            for k in range(2):                     # 先试最多的，不行再试第二多的
                n, ch = cnt[k]
                if n > 0 and res[-2:] != [ch, ch]: # 放 ch 会不会造成三连？
                    res.append(ch)
                    cnt[k][0] -= 1
                    break
            else:                                  # 两个都放不了 → 结束
                return "".join(res)
