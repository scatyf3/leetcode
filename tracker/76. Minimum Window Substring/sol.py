class Solution:
    def minWindow(self, s: str, t: str) -> str:
        def valid(cnt):
            res = True
            for key in cnt:
                if cnt[key]>0:
                    return False
            return res
        cnt = Counter(t)
        l = 0
        len_t=len(t)
        if len_t>len(s):
            return ""
        cur_slice=""
        len_cur_slice=len(s)+1 # larger than all
        for r in range(0,len(s)):
            if s[r] in cnt: #update r
                cnt[s[r]]-=1
            while valid(cnt): 
                if r-l+1<len_cur_slice:
                    len_cur_slice=r-l+1
                    cur_slice=s[l:r+1]
                if s[l] in cnt:
                    cnt[s[l]]+=1
                l+=1
        return cur_slice


        
