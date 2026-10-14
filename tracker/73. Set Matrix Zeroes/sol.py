class Solution:
    def setZeroes(self, matrix: list[list[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        zero_row = set()
        zero_col = set()

        for row in range(len(matrix)):
            for col in range(len(matrix[0])):
                if matrix[row][col]==0:
                    zero_row.add(row)
                    zero_col.add(col)
        #print(zero_row)
        #print(zero_col)
        for row in range(len(matrix)):
            if row in zero_row:
                # print(row)
                for col in range(len(matrix[0])):
                    #print(row,col)
                    matrix[row][col]=0
        for col in range(len(matrix[0])):
            if col in zero_col:
                # print(col)
                for row in range(len(matrix)):
                    #print(row,col)
                    matrix[row][col]=0


