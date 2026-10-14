class Solution:
    def findAnagrams(self, s: str, p: str) -> list[int]:
        '''
        sliding windows
        p => cnt for our neet
        edit cnt based on sliding windows on s
        '''
        cnt = Counter(p)
        l = 0
        len_p = len(p)
        #if s[l] in cnt:
        #            cnt[s[l]]+=1

        def is_valid(cnt):
            for key in cnt:
                if cnt[key]!=0:
                    return False
            return True
        res = []
        for r in range(0,len(s)):
            #print(r)
            if s[r] in cnt: # sliding windows要先add再检查，并且只有sliding windows是左闭右闭
                cnt[s[r]]-=1
            while r-l+1>len_p: #cur r-l+1=0
                #print(l)
                if s[l] in cnt:
                    cnt[s[l]]+=1
                l+=1

            if is_valid(cnt):
                res.append(l)
                # print(s[l:r+1])
                # print(cnt)

        return res
