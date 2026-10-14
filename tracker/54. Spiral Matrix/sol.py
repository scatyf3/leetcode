class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        res = []
        # 为啥这里闭区间（ => 好递推
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        while top <= bottom and left <= right:
            i = left
            # ⬆️
            while i<=right and top <= bottom and left <= right:
                res.append(matrix[top][i])
                i+=1
            top+=1
            # ➡️
            j = top
            while j<=bottom and top <= bottom and left <= right:
                res.append(matrix[j][right])
                j+=1
            right-=1
            # ⬇️
            i = right
            while i>=left and top <= bottom and left <= right:
                res.append(matrix[bottom][i])
                i-=1
            bottom-=1
            # ⬅️
            j = bottom
            while j>=top and top <= bottom and left <= right:
                # print(left,j)
                res.append(matrix[j][left])
                j-=1
            left+=1
        return res
            