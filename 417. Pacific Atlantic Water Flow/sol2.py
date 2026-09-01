from collections import deque
from typing import List


class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        '''
        同 sol1, 但用多源 BFS 迭代实现, 避免递归深度问题。
        O(m*n) 时间 / O(m*n) 空间。

        "多源"的含义: 把整条边界一次性全塞进队列当作第 0 层,
        等价于虚构一个"海洋"超级节点连向所有边界格子, 然后从它做单源 BFS。
        这是 BFS 相对 DFS 更自然的地方 —— 不用像 sol1 那样逐个起点重复调用。
        '''
        if not heights or not heights[0]:
            return []

        m, n = len(heights), len(heights[0])

        def bfs(starts: List[tuple]) -> set:
            visited = set(starts)             # 起点无条件入选
            q = deque(starts)
            while q:
                r, c = q.popleft()
                h = heights[r][c]
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < m and 0 <= nc < n):
                        continue
                    if (nr, nc) in visited:
                        continue
                    if heights[nr][nc] < h:   # 逆流: 邻居必须不比当前低
                        continue
                    visited.add((nr, nc))     # 入队即标记, 防止同一格重复入队
                    q.append((nr, nc))
            return visited

        pac_starts = [(0, c) for c in range(n)] + [(r, 0) for r in range(m)]
        atl_starts = [(m - 1, c) for c in range(n)] + [(r, n - 1) for r in range(m)]

        return [list(cell) for cell in bfs(pac_starts) & bfs(atl_starts)]

        '''
        为什么这题 BFS 和 DFS 完全等价(不像最短路那样只能 BFS):
        我们只关心"可达性"这个布尔量, 不关心步数, 所以遍历顺序无所谓。
        选 BFS 纯粹是工程理由: 200x200 全同高度时 DFS 递归深度 4e4 会爆栈。

        注意 visited 的标记时机是"入队时"而不是"出队时"。
        出队才标记的话, 同一个格子会被多个邻居重复推进队列, 退化成指数级。
        '''
