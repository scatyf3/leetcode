class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        m, n = len(grid), len(grid[0])
        DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        cnt = 0
        for r in range(m):
            for c in range(n):
                if grid[r][c] != "1":
                    continue
                cnt += 1                      # 碰到一块没沉的陆地 = 一座新岛
                grid[r][c] = "0"              # 入队即沉
                q = deque([(r, c)])
                while q:
                    cr, cc = q.popleft()
                    for dr, dc in DIRS:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == "1":
                            grid[nr][nc] = "0"
                            q.append((nr, nc))
        return cnt
