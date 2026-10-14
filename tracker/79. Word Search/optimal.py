class Solution:
    def exist(self, board: list[list[str]], word: str) -> bool:
        m, n = len(board), len(board[0])

        def dfs(x, y, i):
            if i == len(word):
                return True
            if not (0 <= x < m and 0 <= y < n) or board[x][y] != word[i]:
                return False
            board[x][y] = '#'
            found = any(dfs(x + dx, y + dy, i + 1) for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
            board[x][y] = word[i]
            return found

        return any(dfs(x, y, 0) for x in range(m) for y in range(n))
