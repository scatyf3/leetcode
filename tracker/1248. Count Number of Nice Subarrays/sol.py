class Solution:
    def numberOfSubarrays(self, nums: list[int], k: int) -> int:
        # sliding windows
        # is called nice if there are k odd numbers on it
        # cnt and sliding windows
        l=0
        cnt=0
        res=0
        for r in range(len(nums)):
            if nums[r]%2==1:
                cnt+=1
            while cnt>k:
                if nums[l]%2==1:
                    cnt-=1
                l+=1
            if cnt==k:
                # backup and shrink left
                l_backup = l
                while nums[l]%2==0:
                    l+=1
                    res+=1
                res+=1
                l=l_backup
        # [2,2,2,1,2,2,1,2,2,2] => valid at right bound

        return res
                
        