class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        remain_part = {}   # remain_value - index
        for idx in range(len(nums)):
            curr=nums[idx]
            # print(curr)
            # print(remain_part)
            if curr in remain_part: # hash table also allow us using in
                return [idx,remain_part[curr]]
            remain = target-curr
            remain_part[remain]=idx
        