class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        idx1=0
        idx2=0
        nums1_copy=nums1.copy()
        # nums1 has a length of m + n
        # but nums1's upper bound is m....
        while(idx1<m and idx2<n):
            if(nums1_copy[idx1]>nums2[idx2]):
                nums1[idx1+idx2]=nums2[idx2]
                # print(nums2[idx2])
                idx2+=1
            else:
                nums1[idx1+idx2]=nums1_copy[idx1]
                # print(nums1_copy[idx1])
                idx1+=1
        if(idx1==m): # we already iterate through nums1 but not nums2
            # move nums 2's element in to finally array
            while(idx2<n):
                nums1[idx1+idx2]=nums2[idx2]
                # print(nums2[idx2])
                idx2+=1  
        if(idx2==n): # we already iterate through nums2 but not nums1
            while(idx1<m):
                nums1[idx1+idx2]=nums1_copy[idx1]
                # print(nums1_copy[idx1])
                idx1+=1  
'''
Error:
1. suboptimal solution
2. forget m's meaning
3. forget to handle tail case
'''
