class Solution:
    def minWindow(self, s: str, t: str) -> str:
        need, win = Counter(t), Counter()
        best, l = "", 0
        for r, c in enumerate(s):
            win[c] += 1
            while win >= need:                    # 多重集包含：win 每个字符都 ≥ need
                if not best or r - l + 1 < len(best):
                    best = s[l:r+1]
                win[s[l]] -= 1
                l += 1
        return best
