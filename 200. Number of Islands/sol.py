class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        cnt=0
        starts=deque()
        visited=set()
        nears=[[-1,0],[1,0],[0,-1],[0,1]]
        # find all 0 as start
        for i in range(len(grid)):
            lst=grid[i]
            for j in range(len(lst)):
                elem=lst[j]
                if grid[i][j]=="1":
                    starts.append((i,j))
        # bfs for all not visited start
        while len(starts)!=0:
            start=starts.popleft()
            if start not in visited:
                # CHANGE: 删掉 print(start)，大输入下 I/O 很慢
                to_be_visit=deque()
                to_be_visit.append(start)
                visited.add(start)  # CHANGE: 入队即标记
                while len(to_be_visit)!=0:
                    curr=to_be_visit.popleft()
                    # CHANGE: 原来在这里 visited.add(curr)（出队才标记）
                    # 同一格在出队前会被多个邻居重复入队，重复的格子又各自扩展邻居，队列爆炸 → TLE
                    for near in nears:
                        next_i=curr[0]+near[0]
                        next_j=curr[1]+near[1]
                        if next_i<len(grid) and next_i>=0 and next_j<len(grid[0]) and next_j>=0:
                            next_pos=(next_i,next_j)
                            if next_pos not in visited and grid[next_pos[0]][next_pos[1]]=="1":
                                visited.add(next_pos)  # CHANGE: 入队即标记
                                to_be_visit.append(next_pos)
                cnt+=1
        return cnt
