class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.

        顺时针 90° = 主对角线转置 + 每行反转
            转置:     (i,j) -> (j,i)
            每行反转:  (i,j) -> (i, n-1-j)
            复合:     (i,j) -> (j, n-1-i)      <- 顺时针 90°
        """
        n = len(matrix)

        # pass 1: 沿主对角线转置。只走上三角 j > i,
        # 否则每对元素会被交换两次,等于没换。
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

        # pass 2: 每行反转(左右镜像)。
        for row in matrix:
            row.reverse()
