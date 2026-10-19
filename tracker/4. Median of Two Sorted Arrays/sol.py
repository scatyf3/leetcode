class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1        # 保证在短的那个上二分
        m, n = len(nums1), len(nums2)
        half = (m + n + 1) // 2               # 左半边的个数（奇数时左边多一个）
        INF = float('inf')

        # 找第一个满足 nums1[k] >= nums2[half-1-k] 的 k，和 35 的 lower_bound 一样
        lo, hi = 0, m - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            # half-mid：nums2左侧元素数
            # half-mid-1：左侧last index
            if nums1[mid] >= nums2[half - 1 - mid]:
                hi = mid - 1
            else:
                lo = mid + 1

        i = lo                                 # nums1 缝右
        j = half - i                           # nums2 缝右

        # mask，防止乱七八糟的判断是否抵达边缘
        # 左mask -inf，右mask +inf
        A_left  = nums1[i-1] if i > 0 else -INF 
        A_right = nums1[i]   if i < m else INF
        B_left  = nums2[j-1] if j > 0 else -INF
        B_right = nums2[j]   if j < n else INF

        if (m + n) % 2 == 1: # 奇数 => 一定是⬅️，因为我们往右走更激进
            return max(A_left, B_left) 
        # 偶数=> 左右缝
        return (max(A_left, B_left) + min(A_right, B_right)) / 2