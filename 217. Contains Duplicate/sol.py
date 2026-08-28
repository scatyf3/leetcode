class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        st = set(nums)
        if(len(nums)!=len(st)):
            return True
        else:
            return False
