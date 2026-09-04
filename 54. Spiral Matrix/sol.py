class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        res = []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1

        while top <= bottom and left <= right:
            for c in range(left, right + 1):          # → 沿 top 行
                res.append(matrix[top][c])
            top += 1

            for r in range(top, bottom + 1):          # ↓ 沿 right 列
                res.append(matrix[r][right])
            right -= 1

            if top <= bottom:                         # 守卫: 还剩至少一行
                for c in range(right, left - 1, -1):  # ← 沿 bottom 行
                    res.append(matrix[bottom][c])
                bottom -= 1

            if left <= right:                         # 守卫: 还剩至少一列
                for r in range(bottom, top - 1, -1):  # ↑ 沿 left 列
                    res.append(matrix[r][left])
                left += 1

        return res