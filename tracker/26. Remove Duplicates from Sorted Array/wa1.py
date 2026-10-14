class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        '''
        input: 
        nums: List[int] with sorted order
        Target: inplace remove same element from sorted array; contain the unique numbers in sorted order.
        return int: vaild prefix end tail_idx
        '''
        n=len(nums) 
        if(n==0):
            return 0
        # tail slice for nums, store invalid remove item in nums[tail:n]
        tail_idx=len(nums)
        s=set() # init a set to keep track dup elements
        # main: iterate through nums's valid prefix [0:tail_index]
        idx=0
        while(idx<tail_idx):
            # print(nums[idx])
            print(tail_idx)
            if(nums[idx] in s):
                s.add(nums[idx])
                # dup, need swap to nums tail
                # swap dup to back
                tmp=nums[idx]
                nums[idx]=nums[tail_idx-1]
                nums[tail_idx-1]=tmp
                tail_idx-=1
                # do not add idx because current newly swapped nums[idx] is not iterated
            else:
                s.add(nums[idx])
                # skip
                idx+=1
            
        return tail_idx

        '''
        dry run
        1. nums=[]
        2. nums=[1,2]
        tail_idx=2
        # idx:0,1, noop
        # return tail_idx=2, means nums is always valid
        while(idx<tail_idx):
            if(nums[idx] in s):
                tmp=nums[idx]
                nums[idx]=nums[tail_idx]
                nums[tail_idx]=tmp
                tail_idex-=1
            else:
                idx+=1
        2. nums=[1,1,2]

        # tail: 3,2(b1),2
        # idx: 0,1(b1),1
        # value: 1,1,2
        while(idx<tail_idx):
            if(nums[idx] in s): # b1
                tmp=nums[idx]
                num[idx]=nums[tail_idx]
                nums[tail_idx]=tmp
                tail_idex-=1
            else: # b1
                idx+=1
        '''
        

'''
Error
1. do not use array is sorted this property
2. ignore the constraint of prefix k element should be sorted order
3. implementation level, forget to consider right timing to add element to set, thus cause wrong result
'''
