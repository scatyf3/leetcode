class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        m, n = len(heights), len(heights[0])
        DIRS = [(1,0),(-1,0),(0,1),(0,-1)]

        p_start = []
        # left-up is the start
        for i in range(0,m):
            p_start.append((i,0))
        for i in range(0,n):
            p_start.append((0,i))

        o_start = []
        # right-down is the start
        for i in range(0,m):
            o_start.append((i,n-1))
        for i in range(0,n):
            o_start.append((m-1,i))

        #print(p_start)
        #print(o_start)


        # def bfs
        # input:start list
        # output: reachable grid or set
        def bfs(start_list):
            q = deque(start_list)
            visited=set(start_list)
            while q:
                q_len=len(q)
                for _ in range(q_len):
                    cur_pos = q.popleft()
                    for nxt in DIRS:
                        next_x = cur_pos[0]+nxt[0]
                        next_y = cur_pos[1]+nxt[1]
                        next_pos = (next_x,next_y)
                        if 0<=next_x<m and 0<=next_y<n and heights[cur_pos[0]][cur_pos[1]]<=heights[next_x][next_y] and next_pos not in visited:
                            q.append(next_pos)
                            visited.add(next_pos)
            return visited
        p_visited = bfs(p_start)
        o_visited=bfs(o_start)
        uni = p_visited & o_visited # not and, need to use &
        return list(uni)
        