class Solution:
    def possibleBipartition(self, n: int, dislikes: list[list[int]]) -> bool:
        # given一个图，link的人不能分成一个组，测试这个图能否被二分
        # 能二分等于无奇数环？
        # 偶数环，tree，chain都能二分
        # 但感觉无非常好的数学解，一个naive的办法是 simulation？从小deg标到大deg？
        # 边多只能说明图里一定有环，不能说明有奇数环
        # if len(dislikes)>n: # 约束大于元素，一定有奇数环
        #     return False

        graph = defaultdict(list) # 直接用这个建图
        for a, b in dislikes: # change graph to index from 0
            graph[a-1].append(b-1)
            graph[b-1].append(a-1)
        # print(graph)

        color = [0] * n              # 0 = 还没分组，1 / -1 = 两个组
        for start in graph.keys():
            if color[start]==0:
                color[start] = 1
                q = deque([start])
                while q:
                    u = q.popleft()
                    for v in graph[u]:
                        if color[v]==0:
                            color[v]=-color[u]
                            q.append(v)
                        elif color[v]==color[u]:
                            return False
        return True