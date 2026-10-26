class Solution:
    def validTree(self, n: int, edges: list[list[int]]) -> bool:
        # has loop or not?
        if len(edges) != n - 1: # n 个点的树，正好有 n − 1 条边。
            return False
        # 在边数等于 n − 1 的前提下，下面三个条件里只要成立一个，另外两个自动成立:
        # 无环，联动，是树
        g = {}
        for edge in edges:
            node1 , node2 = edge 
            if node1 in g:
                g[node1].append(node2)
            else:
                g[node1]=[node2]
            if node2 in g:
                g[node2].append(node1)
            else:
                g[node2]=[node1]
        # {0: [1, 2, 3], 1: [0, 4], 2: [0], 3: [0], 4: [1]}
        # 判断联通性，从任何一个点都能走通，双向链接允许我们从leaf往root走
        visited = {0}
        q = deque([0])
        while q:
            cur = q.popleft()
            for nxt in g.get(cur, []):
                if nxt not in visited:
                    visited.add(nxt)
                    q.append(nxt)
        return len(visited) == n



        