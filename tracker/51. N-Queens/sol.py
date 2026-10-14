class Solution:
    def solveNQueens(self, n: int) -> list[list[str]]:
        res, path = [], []            # path[r] = 第 r 行的皇后放在第几列
        cols, diag, anti = set(), set(), set()   # 已被占的列 / 主对角线 / 副对角线

        def dfs(r):                   # r = 当前要放第几行
            if r==n:                  # ② 结算条件：什么时候放完了？
                res.append(["." * c + "Q" + "." * (n - c - 1) for c in path])
                return
            for c in range(n):        # ① 本层的选项：这一行的每一列
                # r - c 不变 =>主对角
                # r + c 不变 =>副对角
                if c in cols or r - c in diag or r+c in anti:     # ③ 剪枝：列、主对角线、副对角线有没有被占
                    continue
                path.append(c)        # 做选择
                cols.add(c); diag.add((r,c)); anti.add((r,c))
                dfs(r+1)             # ④ 去下一层
                path.pop()            # 撤销
                cols.remove(c); diag.remove(r - c); anti.remove(r+c)

        dfs(0)
        return res
