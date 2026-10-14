class Solution:
    def orangesRotting(self, grid: List[List[int]]) -> int:
        q = deque()
        m = len(grid)
        n = len(grid[0])
        fresh_counter=0 # 错1: 一开始没计数, BFS 走不到的孤立新鲜橘子没法判 -1
        for i in range(m):
            for j in range(n):
                if grid[i][j]==2:
                    q.append((i,j))
                if grid[i][j]==1:
                    fresh_counter+=1

        nxt = [(0,1),(0,-1),(1,0),(-1,0)]
        max_len=0
        while len(q)!=0 and fresh_counter > 0:
            # 错2: 原来只写 while q + max_len=-1, 数的是层数不是分钟数; 最后一层不会再腐烂任何橘子
            # -1 在 [[0]] 挂 (返回 -1), 0 在 [[2]] 挂 (返回 1); 加 fresh_counter>0 就不会多跑那一轮
            cur_layer_len = len(q)
            while cur_layer_len>0:
                cur = q.popleft()
                for offset in nxt:
                    next_pos = (cur[0]+offset[0],cur[1]+offset[1])
                    if 0<=next_pos[0]<m and 0<=next_pos[1]<n and grid[next_pos[0]][next_pos[1]]==1:
                        q.append(next_pos)
                        grid[next_pos[0]][next_pos[1]]=2
                        # 错3: 原来是出队才设 2, 同一格会跨层重复入队, 多算一层, 如 [[2,1,1,2]] 返回 2
                        fresh_counter-=1
                cur_layer_len-=1
            max_len+=1
        if fresh_counter!=0:
            return -1
        else:
            return max_len
