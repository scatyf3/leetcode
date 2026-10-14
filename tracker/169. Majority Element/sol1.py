class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        counter = {}
        for elem in nums:
            if elem not in counter:
                counter[elem]=1
            else:
                counter[elem]+=1
        max_key = 0
        max_value = -1
        for key, value in counter.items(): #.item
            if value>max_value:
                max_value=value
                max_key=key
        return max_key
    
    