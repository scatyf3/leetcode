class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()                                   # ← 一切的前提
        print(nums)
        n = len(nums)
        res = []
        for first_idx in range(n - 2): # 给下面两个pointer留空间
            if nums[first_idx]>0: # 提前退出
                continue
            if nums[first_idx]==nums[first_idx-1] and first_idx>0:
                continue

            l = first_idx+1
            r = n-1
            target = -nums[first_idx]
            while(l<r and r<n):
                if nums[l]+nums[r]>target:
                    r-=1
                elif nums[l]+nums[r]<target: 
                    l+=1
                elif nums[l]+nums[r]==target:
                    res.append([nums[first_idx],nums[l],nums[r]])
                    # skip
                    cur_l_val=nums[l]
                    # print(first_idx,l,r)
                    while nums[l]==cur_l_val and r<n and l<r:
                        l+=1
        return res