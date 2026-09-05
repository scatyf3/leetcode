class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        '''
        Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].

        1d dp for partial mul?

        no, mul is reversable, thus just get global prod and div nums[i]

        the hard part is to handle 0 correctly

        ok，1d dp make sense, for div is too tricky and it is actually not allowed
        '''

        n = len(nums)
        prefix_mul = [1 for i in range(n+1)] # size of n+1,defined as idx's prefix
        suffix_mul = [1]
        for i in range(n):
            prefix_mul[i+1] = prefix_mul[i] * nums[i] 
        for i in range(n):
            suffix_mul.insert(0,suffix_mul[0]*nums[n-i-1])
        # print(prefix_mul)
        # print(suffix_mul)
        '''
        [1,2,3,4]
        [1 ,1 ,2,6, 24]
        [24,24,12,4,1]
        对的，这里写对了，但怎么用？需要得到
        [24,12,8,6]

        其实可以视作掐头去尾，suffix和prefix第一个和最后一个invalid
        [_ ,1 ,2,6, 24]
        [24,24,12,4,_]
        '''
        res = []
        for i in range(n):
            res.append(prefix_mul[i]*suffix_mul[i+1])
        return res
