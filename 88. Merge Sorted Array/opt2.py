class Solution:
    def merge(self, nums1, m, nums2, n):
        i = m - 1          # nums1 effective tail
        j = n - 1          # nums1 effective tail
        k = m + n - 1      # total, and we start from the end of nums1, which is the largest element
        # just consider put every nums2 element into nums1
        while j >= 0:  
            # case1: nums1 is larger than nums2, we need to put nums1's element into nums1                    
            if i >= 0 and nums1[i] > nums2[j]:
                nums1[k] = nums1[i]
                i -= 1
            # case2: nums2 is larger than nums1, we need to put nums2's element into nums1
            else:
                nums1[k] = nums2[j]
                j -= 1
            k -= 1