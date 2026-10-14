from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        dq = deque()          # 存 index；对应的值从队首到队尾严格递减，队首 = 当前窗口最大
        res = []

        for i, x in enumerate(nums):
            # ① 队尾：清掉被 x 支配的候选（比 x 老、又不比 x 大）
            while dq and nums[dq[-1]] <= x:     # < 也能 AC，<= 队列更短
                dq.pop()
            # ② 入队
            dq.append(i)
            # ③ 队首：窗口是 [i-k+1, i]，i-k 那一格刚滑出去
            if dq[0] <= i - k:                  # 改：原来是 dq[0] < i
                dq.popleft()
            # ④ 从 i = k-1 起窗口才满
            if i >= k - 1:                      # 改：原来是 dq[0]-dq[-1]==k
                res.append(nums[dq[0]])         # 改：最大值在队首，不在队尾

        return res
