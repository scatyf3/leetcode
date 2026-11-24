from collections import deque
from typing import List

class Solution:
    def buildMatrix(self, k: int, rowConditions: List[List[int]], colConditions: List[List[int]]) -> List[List[int]]:

        def topo(conditions: List[List[int]]) -> List[int]:
            # build graph: nodes 1..k
            graph = {}
            indeg = [0 for i in range(k+1)]
            for src,dst in conditions:
                if src in graph:   
                    graph[src].append(dst)
                else:
                    graph[src]=[dst]
                indeg[dst]+=1


            # Kahn: start from indegree 0
            # ignore 0
            q = deque([node for node in range(1,len(indeg)) if indeg[node]==0])
            order = []
            while q:
                cur=q.popleft()
                order.append(cur)
                if cur in graph:
                    for nxt in graph[cur]:
                        if indeg[nxt]-1==0:
                            q.append(nxt)
                        indeg[nxt]-=1
            # cycle check
            if len(order)<k:
                return []
            
            return order

        row_order = topo(rowConditions)
        col_order = topo(colConditions)
        # either empty -> return []
        if len(row_order)==0 or len(col_order)==0:
            return []
        # print(row_order)
        # print(col_order)
        # order -> pos[x]
        # order to index? but how
        r = [0] * (k + 1)
        for i, x in enumerate(row_order):
            r[x] = i

        c = [0] * (k + 1)
        for i, x in enumerate(col_order):
            c[x] = i

        # fill k x k matrix
        ans = [[0] * k for i in range(1,k+1)]
        for x in range(1, k + 1):
            ans[r[x]][c[x]] = x
        return ans