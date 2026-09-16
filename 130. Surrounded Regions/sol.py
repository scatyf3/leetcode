class Solution:
    def solve(self, board: List[List[str]]) -> None:
        m, n = len(board), len(board[0])
        q = deque()
        for i in range(m):
            for j in range(n):
                if (i in (0, m-1) or j in (0, n-1)) and board[i][j] == 'O':
                    board[i][j] = '#'              # 边界上的 O，入队即标记
                    q.append((i, j))

        while q:                                   # 多源 BFS，把和边界连通的 O 都标成 #
            x, y = q.popleft()
            for nx, ny in (x+1, y), (x-1, y), (x, y+1), (x, y-1):
                if 0 <= nx < m and 0 <= ny < n and board[nx][ny] == 'O':
                    board[nx][ny] = '#'
                    q.append((nx, ny))

        for i in range(m):                         # # 是安全的，还原成 O；剩下的全部是 X
            for j in range(n):
                board[i][j] = 'O' if board[i][j] == '#' else 'X'
