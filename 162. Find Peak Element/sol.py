class Solution:
    def findPeakElement(self, nums: list[int]) -> int:
        n = len(nums)
        l, r = 0, n - 1
        while l <= r:
            mid = (l + r) // 2
            if mid + 1 < n and nums[mid] < nums[mid + 1]:
                l = mid + 1      # 往右是上坡：峰在右边
            else:
                r = mid - 1      # 往右是下坡（或 mid 已是最后一个）：峰在 mid 或左边
        return l

        '''
        单调栈？但好像不是O(logn)，也不用，如果非要搞的话 size=3的naive sw就行
        这里也没有valid的t/f之分，但binary search一定需要全局有序吗？
        答案一定在还没排除的区间 [l, r] 里
        这句话里没有「有序」两个字。二分每一步只需要做到：扔掉一半之后，剩下那一半里仍然保证有答案。 有序只是做到这一点最常见的方式。

        如果往右是上坡，右半边一定有峰吗？为什么？ 
        一定有，因为最差就是当前+1

        nums = [1, 3, 2, 4, 1]
        上坡?    T  F  T  F  F     ← 不单调，有两处 T→F

        但这里如何保证可以一半一半的从array里丢东西
        被丢掉的那一半里也可能有峰，没关系。只要能保证留下来的那一半一定有峰就够了。
        两个都看 
        '''

        