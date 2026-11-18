class Solution:
    def calcEquation(self, equations: List[List[str]], values: List[float], queries: List[List[str]]) -> List[float]:
        g = {} # src [(dst,val)], bidirection graph 
        # ["a","b"] 2.0 , b->a 1/2.0

        for idx,eq in enumerate(equations):
            value=values[idx]
            src,dst=eq
            if src in g:
                g[src].append((dst,value))
            else:
                g[src]=[(dst,value)]
            if dst in g: 
                g[dst].append((src,1/value))
            else:
                g[dst]=[(src,1/value)]
        # print(g)
        def bfs(start,target):
            if start not in g:
                return -1
            q = deque([(start,1)])
            visited={start:1}
            while q:
                q_len=len(q)
                for _ in range(q_len):
                    cur_node,cur_val=q.popleft()
                    # print(cur_node)
                    next_list=g[cur_node]
                    for next_node, next_value in next_list:
                        if next_node not in visited:
                            q.append((next_node,cur_val*next_value))
                            visited[next_node] = cur_val*next_value
            if target in visited:
                return visited[target]
            else:
                return -1
        res=[]
        for start,target in queries:
            res.append(bfs(start,target))
        return res
