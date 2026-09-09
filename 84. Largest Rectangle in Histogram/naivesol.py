class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n, best = len(heights), 0
        for i in range(n):
            h = heights[i]
            l = r = i
            while l - 1 >= 0 and heights[l - 1] >= h: l -= 1
            while r + 1 < n and heights[r + 1] >= h: r += 1
            best = max(best, h * (r - l + 1))
        return best