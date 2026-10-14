class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        """
        input: nums, k(step to rotate)
        inplace change nums

        sweep between
        [0:n-k] prefix <=> [n-k:n] suffix
        eg: n-k=7-3=4
        [0:4] for prefix, [4:7] for suffix
        """
        n = len(nums)
        k=k%n # use valid k instead of k>n
        if(n==1):
            return
        # save suffix
        suffix = []
        for i in range(n-k,n):
            suffix.append(nums[i])
        # print(suffix)
        
        # push prefix to back
        # start from back to avoid overwrite
        for i in range(n-k-1,-1,-1):
            nums[i+k]=nums[i]
        
        # put suffix to front
        for i in range(0,k): # n=7, k=3 => n-k=4
            # print(i)
            nums[i]=suffix[i]
        