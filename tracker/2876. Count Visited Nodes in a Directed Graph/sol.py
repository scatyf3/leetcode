class Solution:
    def countVisitedNodes(self, edges: List[int]) -> List[int]:
        # edges index => value, src=>dst
        # 函数图：每个点恰好一条出边；每个连通分量恰好一个环（整张图可能有多个环）
        n = len(edges)
        res = [0 for i in range(n)]

        # indeg（edges 本身就是图）
        indeg = [0] * n
        for dst in edges:
            indeg[dst] += 1

        # Kahn：删掉不在环上的点
        q = deque(i for i in range(n) if indeg[i] == 0)

        # ✗ set 丢顺序；offset 是「离叶子多远」，不是「离环多远」
        # removed = set()
        # for i in range(n):
        #     if indeg[i] == 0:
        #         removed.add((i,0))
        # chain_offset=1
        # while q:
        #     qlen=len(q)
        #     for _ in range(qlen):
        #         node = q.popleft()
        #         nxt = edges[node]
        #         indeg[nxt] -= 1
        #         if indeg[nxt] == 0:
        #             q.append(nxt)
        #             removed.add((nxt,chain_offset))
        #     chain_offset+=1

        # ✓ 只记出队顺序（叶子 → 环），不用分层
        removed = list(q)             # 初始叶子
        while q:
            node = q.popleft()
            nxt = edges[node]
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
                removed.append(nxt)   # 和入队绑在一起
        # 此时 indeg > 0 的点都在环上
        # ans = [0] * n    # ✗ 没用到，返回的是 res

        # TODO 1: 环上的点
        # ✗ 把所有环的点数加在一起了
        # cnt=0
        # for i in range(n):
        #     if indeg[i] != 0:
        #         cnt+=1
        # for i in range(n):
        #     if indeg[i] != 0:
        #         res[i]=cnt
        # print(removed)
        # removed是在环里的
        # ✓ 每个环走一圈，用自己的长度；res[i] == 0 表示这个环还没走过
        for i in range(n):
            if indeg[i] != 0 and res[i] == 0: # removed
                cycle = [i]
                cur = edges[i]
                while cur != i:
                    cycle.append(cur)
                    cur = edges[cur]
                for node in cycle:
                    res[node] = len(cycle)

        # print(chain_offset)    # ✗ 调试输出

        # TODO 2: 不在环上的点
        # ✗ chain_len 只对最长的那条链成立
        # chain_len=chain_offset-1
        # for node,offset in removed:
        #     res[node]=cnt+chain_len-offset

        # ✓ 倒序（环 → 叶子），算 node 时 res[edges[node]] 一定已经有了
        # remove是先remove远的再remove近的，所以反过来
        # 永远是远=>近递推，这样chain最近的看环，以此类推
        for node in reversed(removed):
            res[node] = res[edges[node]] + 1

        return res