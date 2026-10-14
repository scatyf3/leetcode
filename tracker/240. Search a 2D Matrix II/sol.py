class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        r, c = 0, len(matrix[0]) - 1          # 从右上角出发
        while r < len(matrix) and c >= 0:
            x = matrix[r][c]
            if x > target:
                c -= 1      # 这一列往下都 ≥ x > target，整列扔掉
            elif x < target:
                r += 1      # 这一行往左都 ≤ x < target，整行扔掉
            else:
                return True
        return False
