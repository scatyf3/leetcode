class Solution:
    def getMaxFunctionValue(self, receiver: List[int], k: int) -> int:
        n = len(receiver)
        pos = list(range(n))     # 从 i 出发，现在走到谁
        score = [0] * n          # 目前得分，不含 pos[i]
        to = receiver            # 走 L 步到谁
        s = list(range(n))       # 走 L 步得分，含起点、不含终点

        while k > 0:
            if k & 1:
                for i in range(n):
                    p = pos[i]
                    score[i] += s[p]
                    pos[i] = to[p]
            # L -> 2L，s 要用旧的 to，所以先更新 s
            s = [s[i] + s[to[i]] for i in range(n)]
            to = [to[j] for j in to]
            k >>= 1

        return max(score[i] + pos[i] for i in range(n))