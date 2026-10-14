class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last_seen_index = {}
        l=0
        max_len=0
        for r,c in enumerate(s):
            if c in last_seen_index:
                l=max(l, last_seen_index[c] + 1) # 这里同时处理边界和非边界
            last_seen_index[c]=r
            max_len=max(r-l+1,max_len) # 正常的距离是r-l+1，然而此时是第一个invalid，然后又要-1
        return max_len