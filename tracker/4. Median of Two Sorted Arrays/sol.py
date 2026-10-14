class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1        # 保证在短的那个上二分
        m, n = len(nums1), len(nums2)
        half = (m + n + 1) // 2               # 左半边的个数（奇数时左边多一个）
        INF = float('inf')

        lo, hi = 0, m                          # i = nums1 贡献给左半边的个数，取值 [0, m]
        while lo <= hi:
            i = (lo + hi) // 2
            j = half - i                           # nums2 贡献多少个

            # 切口两侧的四个数，越界的用 ±inf 补
            L1 = nums1[i - 1] if i > 0 else -INF
            R1 = nums1[i]     if i < m else  INF
            L2 = nums2[j - 1] if j > 0 else -INF
            R2 = nums2[j]     if j < n else  INF

            if L1>R2:                           # nums1 左边那个太大 → i 切多了
                hi = i-1
            elif R1<L2:                         # nums2 左边那个太大 → i 切少了
                lo = i+1
            else:                              # 两对交叉都满足 ≤，切对了
                left_max = max(L1,L2)
                if (m + n) % 2 == 1:
                    return float(left_max)
                right_min = min(R1,R2)
                return (left_max + right_min) / 2
