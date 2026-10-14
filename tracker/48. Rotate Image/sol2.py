class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.

        一趟版:直接按四元环搬运,不做两次全扫描。

        顺时针 90° 的映射 (i,j) -> (j, n-1-i) 的阶是 4,
        套 4 次回到原点,所以每个元素属于一个 4 元环:

            (i,j) -> (j, n-1-i) -> (n-1-i, n-1-j) -> (n-1-j, i) -> (i,j)

        一个临时变量就能把这 4 个位置轮转好。
        下面用 pull 形式写:每个位置去拿它该拿的那个,
        即 new[a][b] = old[n-1-b][a]。
        """
        n = len(matrix)

        # 遍历范围只取左上角一块,保证每个环恰好被处理一次。
        # 注意行列不对称:i 走 n//2,j 走 (n+1)//2。
        #   n=3 -> i∈{0}, j∈{0,1}   2 个环 x 4 = 8 个元素 + 中心 1 个 = 9
        #   n=4 -> i∈{0,1}, j∈{0,1} 4 个环 x 4 = 16
        # 若 j 也写成 n//2,n 为奇数时会漏掉中间那一列的上半段。
        for i in range(n // 2):
            for j in range((n + 1) // 2):
                tmp = matrix[i][j]
                matrix[i][j]             = matrix[n-1-j][i]
                matrix[n-1-j][i]         = matrix[n-1-i][n-1-j]
                matrix[n-1-i][n-1-j]     = matrix[j][n-1-i]
                matrix[j][n-1-i]         = tmp
