from typing import List


class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        '''
        Input:
        - heights: List[List[int]], m x n 矩阵, 1 <= m,n <= 200, 0 <= heights[r][c] <= 1e5
                   heights[r][c] = 该格海拔
        Target: 找出所有"雨水既能流到太平洋、也能流到大西洋"的格子
                太平洋 = 上边界 + 左边界; 大西洋 = 下边界 + 右边界
                水的流向规则: 只能流向四邻中海拔 <= 自己 的格子(可以平着流)
        Return: 这些格子的坐标列表, 顺序任意
        Output: List[List[int]]

        解法: 从两个海洋的边界反向 DFS  O(m*n) 时间 / O(m*n) 空间

        为什么不能 DP(这是本题唯一的坑, 见 note.md):
        DP 要求依赖无环、能排出计算顺序。但水四个方向都能流,
        (r,c) 能不能到太平洋可能取决于右边/下边的格子, 而它们又可能取决于 (r,c)
        -> 依赖成环 -> 没有任何行列扫描顺序能算对。

        破法: 反着问。
        不问"谁能流到海", 改问"从海边出发, 逆流而上能爬到哪些格子"。
        逆流的条件是 邻居 >= 当前, 高度沿路径单调不减 -> 天然无环, 可以安全搜索。
        两个海洋各搜一遍, 取交集就是答案。
        '''
        if not heights or not heights[0]:
            return []

        m, n = len(heights), len(heights[0])
        pacific, atlantic = set(), set()      # 各自存"能逆流爬到"的格子

        def dfs(r: int, c: int, visited: set, prev: int) -> None:
            '''
            从 (上一个格子, 高度 prev) 逆流走到 (r,c)。
            prev 是"水流下来的那一侧"的高度, 所以能逆流上来的条件是 heights[r][c] >= prev。
            '''
            if r < 0 or r >= m or c < 0 or c >= n:
                return                        # 出界
            if (r, c) in visited:
                return                        # 已标记过, 剪枝(也顺手防了平地互相往返)
            if heights[r][c] < prev:
                return                        # 比来的地方低 -> 水流不上来

            visited.add((r, c))
            h = heights[r][c]
            dfs(r + 1, c, visited, h)
            dfs(r - 1, c, visited, h)
            dfs(r, c + 1, visited, h)
            dfs(r, c - 1, visited, h)

        # 起点传自己的高度, 等价于"起点无条件入选"
        for c in range(n):
            dfs(0, c, pacific, heights[0][c])            # 上边界 -> 太平洋
            dfs(m - 1, c, atlantic, heights[m - 1][c])   # 下边界 -> 大西洋
        for r in range(m):
            dfs(r, 0, pacific, heights[r][0])            # 左边界 -> 太平洋
            dfs(r, n - 1, atlantic, heights[r][n - 1])   # 右边界 -> 大西洋

        return [list(cell) for cell in pacific & atlantic]

        '''
        Dry Run: 那个证明 DP 会错的 3x3 反例
            9 9 1
            9 5 2
            9 9 9
          关键格子是 (1,1)=5 —— 它既不在第一行也不在第一列, 所以 base case 救不了它。
          正向看: 上邻(0,1)=9 和 左邻(1,0)=9 都比它高, 流不过去;
                  但往右流到 (1,2)=2, 再往上流到 (0,2)=1, (0,2) 在第一行 -> 到太平洋。
          反向搜索是怎么抓到它的:
            (0,2)=1 起点(上边界) -> 入 pacific
                    -> (1,2)=2 >= 1 爬得上去 -> 入 pacific
                            -> (1,1)=5 >= 2 爬得上去 -> 入 pacific   <- 抓到了
            逆流方向和水流方向恰好相反, 所以"水往右往上流出去"就等价于"从海往左往下爬回来"。

        Test Cases:
        [[1]]                      -> [[0,0]]        单格同时贴两个海
        [[1,1],[1,1]]              -> 全部           平地随便流
        [[1,2,2,3,5],
         [3,2,3,4,4],
         [2,4,5,3,1],
         [6,7,1,4,5],
         [5,1,1,2,4]]              -> LC 官方样例, 7 个格子
        单行 [[1,2,3]] / 单列       -> 每个格子都同时贴上下(或左右)两个海 -> 全部
        严格递减的一行 [[5,4,3,2,1]] -> 也是全部(单行时上下边界都成立)
        200x200 全同高度            -> 递归深度可达 4e4, Python 默认 1000 会 RecursionError
                                      -> 用 sol2.py 的迭代 BFS 版本更稳
        '''
