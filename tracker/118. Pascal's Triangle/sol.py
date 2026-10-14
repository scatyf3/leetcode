class Solution:
    def generate(self, numRows: int) -> list[list[int]]:
        res = []
        if numRows==1:
            return  [[1]]

        res = [[1],[1,1]]
        for i in range(2,numRows):
            l=0
            r=1
            row = [1]
            while r<i:
                # print(l,r)
                row.append(res[-1][l]+res[-1][r])
                l+=1
                r+=1
            row.append(1)
            res.append(row)
        return res
