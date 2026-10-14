class Solution:
    def nextGreaterElement(self, n: int) -> int:
        # next permutation
        num_list_q = deque()
        while n!=0:
            cur=n%10
            n=n//10
            num_list_q.appendleft(cur)
        n=len(num_list_q)
        nums=list(num_list_q)
        i=n-2
        while  i>=0 and nums[i]>=nums[i+1]:
            i-=1
        # find nearest j larger than i
        if i==-1:
            return -1
        j=n-1
        while nums[j]<=nums[i]:
            j-=1
        nums[j],nums[i]=nums[i],nums[j]
        # swap between i and n, nums[j]是最小比nums[i]大的
        # +permutation 元素唯一，此时后缀仍然是降序
        # swap之后一定比原来大，我们让他变升序，是最小的最大
        # 但是在permutation里有保障，这里没有保障，可能有bug
        l = i+1
        r = n-1
        # print(l,r) # 1,1
        while l<=r:
            nums[l],nums[r]=nums[r],nums[l]
            l+=1
            r-=1
        res = 0
        for idx in range(n):
            # print(nums[idx])
            res = res * 10 + nums[idx]
        return res if res <= 2**31 - 1 else -1


