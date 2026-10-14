class Solution:
    def exist(self, board: list[list[str]], word: str) -> bool:
        '''
        grid dfs
        '''
        m, n = len(board), len(board[0])
        start = []

        for i in range(m):
            for j in range(n):
                if board[i][j]==word[0]:
                    start.append((i,j))
        
        nxt = [(0,1),(0,-1),(1,0),(-1,0)]
        find = False
        def dfs(x,y,remain):
            nonlocal find
            if remain==len(word):
                find=True
                return
            for offset in nxt:
                next_x = offset[0]+x
                next_y = offset[1]+y
                if 0<=next_x<m and 0<=next_y<n and (next_x,next_y) not in visited and board[next_x][next_y]==word[remain]:
                    visited.add((next_x,next_y))
                    dfs(next_x,next_y,remain+1)
                    visited.remove((next_x,next_y))

        for pair in start:
            visited=set()
            visited.add(pair)
            dfs(pair[0],pair[1],1)

        return find