class Solution:
    def maximumInvitations(self, favorite: list[int]) -> int:
        # build graph
        #print(favorite)
        n=len(favorite)
        #print(n)
        g = {}
        indeg = [0 for i in range(len(favorite))]
        timestamp = [-1 for i in range(len(favorite))]
        for src, dst in enumerate(favorite):
            if src in g:
                g[src].append(dst)
            else:
                g[src]=[dst]
            indeg[dst]+=1
        # 1. 剥叶子：顺手记"走到每个点的最长链"
        depth = [0] * n
        q = deque(i for i in range(n) if indeg[i] == 0)
        while q:
            cur = q.popleft()
            for nxt in g[cur]:
                depth[nxt] = max(depth[nxt], depth[cur] + 1)  # 环上的点也会被更新
                indeg[nxt] -= 1                                # 先减
                if indeg[nxt] == 0:                            # 再判
                    q.append(nxt)

        # 2. 量环：剩下 indeg > 0 的都在环上，每个环走一圈
        max_loop = 0
        pair_sum = 0
        for i in range(n):
            if indeg[i] == 0:
                continue
            size, j = 0, i
            while indeg[j] > 0:
                indeg[j] = 0          # 当 visited 用
                size += 1
                j = favorite[j]
            # 3. 两种桌子
            if size == 2:
                pair_sum += 2 + depth[i] + depth[favorite[i]]
            else:
                max_loop = max(max_loop, size)

        return max(max_loop, pair_sum)