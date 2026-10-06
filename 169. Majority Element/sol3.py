class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        counter = 0
        for idx in range(0,len(nums)):
            if counter == 0:
                maj=nums[idx]
                counter=1
            else: #counter>0
                if nums[idx]==maj:
                    counter+=1
                else:
                    counter-=1
        return maj
        