class Solution:
    def totalFruit(self, fruits: list[int]) -> int:
        # cnt => top2
        cnt = Counter()
        # 枚举r，根据cnt状态收缩l
        l=0
        r=0
        res=0
        while r<len(fruits):
            cnt[fruits[r]]+=1
            while len(cnt)>2 and l<=r: # directly move l instead of select a fruit to evict
                cnt[fruits[l]]-=1
                if cnt[fruits[l]]==0:
                    del cnt[fruits[l]]
                l+=1
            # valid
            res=max(res,r-l+1)
            r+=1
        return res
        