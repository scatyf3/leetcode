class Solution:
    def majorityElement(self, nums):
        count = 0
        candidate = None
        for num in nums:
            if count == 0:        # curr element is eliminate
                candidate = num # random select elem
            count += 1 if num == candidate else -1 # modify count
        return candidate

'''
space from O(n) to O(1)
Since problem tell us that majority must exist, we can pair different element and eliminate different one
Eg:
[1,1,2] => [1]
[1,2,3,3] =>[3,3]
'''


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        maj = nums[0]
        counter = 1
        for idx in range(1,len(nums)):
            if counter == 0: #next iter after elem!=maj
                # print("change major")
                maj=nums[idx]
            if nums[idx]!=maj:
                # print("neq")
                counter -=1
            else:
                # print("eq")
                counter+=1
        return maj


