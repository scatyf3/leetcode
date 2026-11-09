# tldr: 不要用2/1思考，每次只care一步，前者分类讨论特别烦人
class Solution:
    def longestDiverseString(self, a: int, b: int, c: int) -> str:
        cnt = {"a": a, "b": b, "c": c}
        res = []
        while True:
            # 默认从小往大，需要reverse
            # 按照value，从大到小迭代key
            for ch in sorted(cnt, key=cnt.get, reverse=True):
                if cnt[ch]==0:  # 这个字符用完了
                    continue
                if len(res) >= 2  and res[-2]==ch and res[-1]==ch:   # 放了会三连
                    continue
                res.append(ch)
                cnt[ch]-=1
                break
            else: # for else，如果for没被break，则进入到当前分支
                return "".join(res)
