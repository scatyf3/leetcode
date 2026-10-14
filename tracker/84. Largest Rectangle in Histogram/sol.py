class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        '''
        trap rain water varient?
        no, max prefix do not make sense in this case
        naive for loop for every hist, expend until get Rectangle smaller
        is expend greedy?
        5 1 1 1 1 1 1 
        no, 5-2-3-4-5-6, 6 is the better

        hint: Monotonic Stack

        need something to store each [l,r] interval minimal, O(n^2/2)
        '''
        n = len(heights)
        stack = []
        best = 0

        for i in range(n + 1): # 枚举每个柱子
            h = 0 if i == n else heights[i]   
            while stack and heights[stack[-1]] >= h: 
                top = stack.pop()
                left = stack[-1] if stack else -1  # left就是之前的最小值index
                width = i - left - 1               # 
                best = max(best, heights[top] * width) # update max
            stack.append(i)

        return best
