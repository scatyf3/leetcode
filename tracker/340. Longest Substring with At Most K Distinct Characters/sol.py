class Solution:
    def lengthOfLongestSubstringKDistinct(self, s: str, k: int) -> int:
        # end at valid => 枚举右，收缩⬅左
        cnt = Counter()
        l=0
        max_len = 0
        for r in range(len(s)):
            cnt[s[r]]+=1
            while len(cnt)>k:
                cnt[s[l]]-=1
                if cnt[s[l]]==0: #remove
                    del cnt[s[l]]
                l+=1
            # valid with nums distinct characters is k
            max_len = max(max_len,r-l+1)
            #print(cnt)
            #print(s[l:r+1])
        return max_len