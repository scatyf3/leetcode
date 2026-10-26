class Solution:
    def wallsAndGates(self, rooms: list[list[int]]) -> None:
        """
        Do not return anything, modify rooms in-place instead.
        """
        # multi root bfs from gates?
        nxt = [(0,1),(0,-1),(1,0),(-1,0)]
        start = []
        for row in range(len(rooms)):
            for col in range(len(rooms[0])):
                if rooms[row][col]==0:
                    start.append((row,col,0))
        q = deque(start)
        while q:
            q_len=len(q)
            for _ in range(q_len):
                cur_x, cur_y, dis = q.popleft() # 递推传dis即可
                for offset in nxt:
                    nxt_x = cur_x+offset[0]
                    nxt_y = cur_y+offset[1]
                    # dis+1也作为条件，否则超时
                    if 0<=nxt_x<len(rooms) and 0<=nxt_y<len(rooms[0]) and rooms[nxt_x][nxt_y]!=0 and rooms[nxt_x][nxt_y]!=-1 and dis+1<rooms[nxt_x][nxt_y]:
                        q.append((nxt_x,nxt_y,dis+1))
                        rooms[nxt_x][nxt_y]=dis+1
        
