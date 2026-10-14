class Solution:
    def trap(self, height: List[int]) -> int:
        n = len(height)
        L = [-1] * n
        R = [-1] * n
        
        # 计算每个位置左边的最大高度
        L[0] = height[0]
        for i in range(1, n):
            L[i] = max(L[i-1], height[i])
        
        # 计算每个位置右边的最大高度
        R[n-1] = height[n-1]
        for i in range(n-2, -1, -1):
            R[i] = max(R[i+1], height[i])
        
        # 计算每个位置能装的水
        total = 0
        for i in range(n):
            water_level = min(L[i], R[i])
            total += water_level - height[i]
        
        return total