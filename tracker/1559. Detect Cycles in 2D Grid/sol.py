class UF:
    def __init__(self):
        self.parent={}
        self.count=0
    def find(self, x):
        if x not in self.parent:             # 什么时候 x 是第一次出现？
            self.parent[x]=x                 # 新节点的父亲是谁？
            self.count+=1                    # count 怎么变？
        while self.parent[x]!=x:         # 什么时候 x 还不是根？
            self.parent[x] = self.parent[self.parent[x]] # optinal的路径压缩：把 x 的父亲改成谁？
            x=self.parent[x]             # x 往上跳一步
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)         # 先找什么？
        if rx==ry:                    # 什么情况说明本来就连通？
            return False             # 返回什么表示"多余的边"？
        self.parent[rx]=ry          # 把谁挂到谁下面？注意要挂"根"
        self.count-=1                        # count 怎么变？
        return True

class Solution:
    def containsCycle(self, grid: list[list[str]]) -> bool:
        m, n = len(grid), len(grid[0])
        # nxt = [(0,1),(0,-1),(1,0),(-1,0)] => 处理两次
        nxt = [(0,1),(1,0)]
        uf = UF()
        for i in range(m):
            for j in range(n):
                for di, dj in nxt:            # TODO: 只看哪几个方向？
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n  and grid[ni][nj] == grid[i][j]:   # TODO: 边界
                        if not uf.union((i, j), (ni, nj)):
                            return True
        return False