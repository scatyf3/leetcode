class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        '''
        naive two sum is O(n)
        given the array is sorted, we should solve this via binary search or O(logn)
        
        no,naive 2 pointer
        exactly one solution => no misc edge case

        1-indexed => +1
        '''
        l=0
        n = len(numbers)
        r=n-1
        while(l<r):
            if numbers[l]+numbers[r]>target:
                r-=1
            elif numbers[l]+numbers[r]<target:
                l+=1
            else:
                return [l+1,r+1]