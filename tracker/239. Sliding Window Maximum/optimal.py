from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        # 定长窗口：进 r，出 r-k，从 r = k-1 起结算
        dq = deque()      # 存下标；对应的值从队首到队尾非严格递减，队首 = 窗口最大
        res = []
        for r, x in enumerate(nums):
            # 进 r：先驱逐被 x 支配的（比 x 老、又不比 x 大）
            while dq and nums[dq[-1]] < x:
                dq.pop()
            dq.append(r)
            # 出 r-k：要么早被支配踢了，要么还在，且一定在队首
            if dq[0] == r - k:
                dq.popleft()
            # 结算：r = k-1 起窗口满
            if r >= k - 1:
                res.append(nums[dq[0]])
        return res
