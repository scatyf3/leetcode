class Solution:
    def merge(self, nums1: list[int], m: int, nums2: list[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        # merge 2 to 1
        write=m+n-1
        read_1 = m-1
        read_2 = n-1
        while read_2>=0:
            if read_1>=0 and nums1[read_1]>nums2[read_2]: 
                nums1[write]=nums1[read_1]
                # print(nums1)
                read_1-=1
                write-=1
            else:
                nums1[write]=nums2[read_2]
                # print(nums1)
                read_2-=1
                write-=1
