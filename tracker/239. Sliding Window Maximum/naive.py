from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        q = deque()
        res = []
        for i, x in enumerate(nums):
            q.append(x)              # 进场
            if len(q) > k:           # 先append再pop防止edge case
                q.popleft()
            if i >= k - 1:           # 窗口满了才结算
                res.append(max(q))   # 每次整窗扫一遍，O(k)
        return res
