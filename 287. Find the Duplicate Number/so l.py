class Solution:
    def findDuplicate(self, nums: List[int]) -> int:
        def scan(nums: List[int],target) -> int:
            cnt=0
            for elem in nums:
                if elem<=target:
                    cnt+=1
            return cnt
        l=1
        r=len(nums)
        # l and r are value
        mid=int((l+r)/2)
        while l<=r:
            cnt=scan(nums,mid)
            #print(cnt)
            #print(mid)
            if cnt>mid: # left, mid already>target
                r=mid-1
            elif cnt<=mid:
                # two or more —— 重复的那个数可以出现 3 次、5 次、n 次。它多占的坑,就是别的值整个缺席腾出来的。缺席的值一多,C(v) 自然可以小于 v。
                l=mid+1
            mid=int((l+r)/2)

        return l # 我们返回l，第一个false


