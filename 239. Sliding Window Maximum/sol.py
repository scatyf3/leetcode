from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        dq = deque()                          # 存下标; 对应的值严格递减
        res = []

        for i, x in enumerate(nums):
            while dq and nums[dq[-1]] <= x:   # ① 队尾: 清掉被 x 支配的候选
                dq.pop()
            dq.append(i)                      # ② 入队
            if dq[0] <= i - k:                # ③ 队首: 清掉过期的
                dq.popleft()
            if i >= k - 1:                    # ④ 窗口满了才结算
                res.append(nums[dq[0]])

        return res

'''

i=0, 进场 3
    名单: [3]
    (窗口还没满 2 个, 不出答案)

i=1, 进场 1
    队尾是 3, 3 > 1, 踢不动 —— 1 还有机会(等 3 走了他可能当老大)
    名单: [3, 1]
    窗口 = [3,1], 老大 = 队首 = 3        -> 答案 3 ✓

i=2, 进场 4
    队尾是 1, 1 <= 4  -> 划掉 1
    队尾是 3, 3 <= 4  -> 划掉 3
    名单空了, 4 进来
    名单: [4]                             <- 一个强者清空整张名单
    窗口 = [1,4], 老大 = 4               -> 答案 4 ✓

i=3, 进场 2
    队尾是 4, 4 > 2, 踢不动
    名单: [4, 2]
    窗口 = [4,2], 老大 = 4               -> 答案 4 ✓
所以dq就是那个名单而不是显式存窗口
'''
