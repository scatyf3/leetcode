class Solution:
    def longestCycle(self, edges: list[int]) -> int:
        # bfs with kahn to remove non-loop
        g = {}
        n = len(edges)
        indeg = [0 for i in range(n)]
        for src,dst in enumerate(edges):
            if dst!=-1: #skip -1
                if src in g:
                    g[src].append(dst)
                else:
                    g[src]=[dst]
                indeg[dst]+=1
            else:
                g[src]=[]
        start=[]
        for dst in range(n):
            if indeg[dst]==0:
                start.append(dst)
        q = deque(start)
        while q:
            cur_node = q.popleft()
            for next_node in g[cur_node]:
                indeg[next_node]-=1
                if indeg[next_node]==0:
                    q.append(next_node)
        all_zeros=True
        cand_st=set()
        cand = []
        for dst in range(n):
            if indeg[dst]!=0:
                all_zeros=False
                cand.append(dst)
                cand_st.add(dst)
        if all_zeros:
            return -1
        visited = set()
        res=0
        for node in cand:
            if node in cand_st:
                cur=0
                q = deque([node])
                while q:
                    cur_node = q.popleft()
                    for next_node in g[cur_node]:
                        if next_node in cand_st:
                            cur+=1
                            q.append(next_node)
                            cand_st.remove(next_node)
            res=max(cur,res)
        return res



            

            
            
