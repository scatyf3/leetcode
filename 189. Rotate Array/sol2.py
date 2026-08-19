class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        """
        reversal method: O(n) time, O(1) space

        rotate right by k == reverse whole, then reverse [0:k], then reverse [k:n]
        eg: [1,2,3,4,5,6,7], k=3
        reverse all:      [7,6,5,4,3,2,1]
        reverse [0:k]:    [5,6,7,4,3,2,1]
        reverse [k:n]:    [5,6,7,1,2,3,4]
        """
        n = len(nums)
        k %= n

        def reverse(l: int, r: int) -> None:
            while l < r:
                nums[l], nums[r] = nums[r], nums[l]
                l += 1
                r -= 1

        reverse(0, n - 1)
        reverse(0, k - 1)
        reverse(k, n - 1)
