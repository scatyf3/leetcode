class Solution:
    def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
        nxt_move=[(0,1),(0,-1),(1,0),(-1,0)]
        mx=0
        for lst_idx in range(len(grid)):
            lst=grid[lst_idx]
            for idx in range(len(grid[0])):
                elem=lst[idx]
                if elem==1: # start
                    cur_size=0
                    q = deque()
                    q.append((lst_idx,idx))
                    # print(lst_idx,lst_idx)
                    while len(q)!=0:
                        cur_pos = q.popleft()
                        # print(cur_pos)
                        if grid[cur_pos[0]][cur_pos[1]]!=0:
                            grid[cur_pos[0]][cur_pos[1]]=0
                            cur_size+=1
                            for nxt in nxt_move:
                                next_lst = cur_pos[0]+nxt[0]
                                next_idx = cur_pos[1]+nxt[1]
                                if 0<=next_lst<len(grid) and 0<=next_idx<len(grid[0]) and grid[next_lst][next_idx]==1:
                                    q.append((next_lst,next_idx))
                    mx=max(mx,cur_size)
        return mx
                    


        