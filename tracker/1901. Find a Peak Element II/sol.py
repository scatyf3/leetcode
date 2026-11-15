class Solution:
    def findPeakGrid(self, mat: list[list[int]]) -> list[int]:
        l=0
        r=len(mat)-1
        while l<=r:
            mid = (l+r)//2
            row = mat[mid]
            col_index, val = max(enumerate(row), key=lambda x: x[1])
            down = mat[mid + 1][col_index] if mid + 1 < len(mat) else -1 # 越界当-1
            up = mat[mid - 1][col_index] if mid - 1 >= 0 else -1
            if down > val:
                l = mid + 1
            elif up > val:
                r = mid - 1
            else:
                return [mid, col_index]
