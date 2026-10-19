class Solution:
    def numDistinctIslands(self, grid: list[list[int]]) -> int:
        nxt = [(0,1),(0,-1),(1,0),(-1,0)]
        islands = []
        cur_island = []
        def dfs(x,y):
            # dfs, set all connected 1 to 0
            nonlocal cur_island
            
            for offset in nxt:
                x_next = x+offset[0]
                y_next = y+offset[1]
                if 0<=x_next<len(grid) and 0<=y_next<len(grid[0]) and grid[x_next][y_next]==1:
                    grid[x_next][y_next]=0
                    dfs(x_next,y_next)  
                    cur_island.append((x_next,y_next)) 
            return cur_island
            
        # cnt=0
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col]==1:
                    islands.append(dfs(row,col)[:])
                    cur_island.clear()
                    # cnt+=1
        # somehow identify if is same
        # move left to (0,0)?
        for idx,island in enumerate(islands): 
            min_x = float("+inf")
            min_y = float("+inf")
            for x,y in island:
                min_x = min(min_x,x)
                min_y = min(min_y,y)
            # print(min_x,min_y)
            for i in range(len(island)):
                islands[idx][i]=(islands[idx][i][0]-min_x,islands[idx][i][1]-min_y)
        shapes = set()
        for island in islands:
            shapes.add(str(island)) #change list to hashable
        return len(shapes)
        
        

        