from collections import deque

# 1. simluation, but this ask us to return [at least] instead of viable path
# 2. dp? but we have snake, where low val depends on high val...
# 3. graph/bfs
class Solution:
    def snakesAndLadders(self, board: list[list[int]]) -> int:
        n = len(board)
        tgt = n * n

        def int_to_pos(val):
            val -= 1
            row_from_bottom = val//n # 从下往上第几行（0 开始）
            col = val%n                  # 先按"从左往右"算
            if row_from_bottom%2==1:      # 什么情况这一行是从右往左？
                col = n - 1 - col               # 镜像
            r = n - 1 - row_from_bottom       # 从下往上的行号 -> 数组下标
            return r, col

        q = deque([(1, 0)])                # (格子编号, 已掷次数)
        visited = {1}

        while q:
            curr, steps = q.popleft()
            for nxt in range(curr+1, min(curr+6,n*n)+1):  # 小心offbyone
                r, c = int_to_pos(nxt)
                if board[r][c]!=-1:                    # nxt 上有蛇/梯子
                    nxt = board[r][c]              # 只跳一次
                if nxt == tgt:
                    return steps+1 # 这里也记得update
                if nxt not in visited:  # 没访问过
                    visited.add(nxt)     # 标记
                    q.append((nxt,steps+1))   # 入队
        return -1