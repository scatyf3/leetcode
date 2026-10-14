class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        def valid(cnt):
            res = True
            for key in cnt:
                if cnt[key]!=0:
                    return False
            return res
        cnt = Counter(s1)
        l = 0
        len_s1=len(s1)
        # print(cnt)
        for r in range(0,len(s2)):
            if s2[r] in cnt: #update r
                cnt[s2[r]]-=1
            while r-l+1>len_s1: # invalid, move l, 这里要求的切片是len一样的切片，而不是包含
                if s2[l] in cnt:
                    cnt[s2[l]]+=1
                l+=1
            if valid(cnt):
                return True
        return False

