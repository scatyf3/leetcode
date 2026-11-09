from collections import deque

class Solution:
    def largestIsland(self, grid: list[list[int]]) -> int:
        n = len(grid)
        DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
        area = {}        # island_id -> size
        island_id = 2    # 从 2 开始编号，为什么？

        # ---------- Pass 1：给每个岛打标签、记面积 ----------
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 1:
                    area[island_id] = self.bfs(grid, r, c, island_id, DIRS)
                    island_id += 1

        # ---------- Pass 2：枚举每个 0 ----------
        ans = max(area.values(), default=0)   # 一个 0 都没有时，答案从哪来？
        for r in range(n):
            for c in range(n):
                if grid[r][c] != 0:
                    continue
                seen = set()
                for dr, dc in DIRS:
                    nr, nc = r + dr, c + dc
                    # TODO: 邻居在界内并且是岛 -> 记下它属于哪个岛
                    # seen就是当前格子如果set1，可能会联通的
                    if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] > 1:
                        seen.add(grid[nr][nc])
                ans = max(ans, 1 + sum(area[i] for i in seen))
        return ans

    def bfs(self, grid, r, c, island_id, DIRS) -> int:
        n = len(grid)
        q = deque([(r, c)])
        grid[r][c] = island_id         # 入队时就标记
        size = 0
        while q:
            # TODO: 出队、计数、把未访问的 1 邻居染色后入队
            r,c=q.popleft()
            size+=1
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc 
                if 0<=nr<n and 0<=nc<n and grid[nr][nc]==1 :
                    q.append((nr,nc))
                    grid[nr][nc]=island_id
        return size
