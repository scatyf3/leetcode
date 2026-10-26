class Solution:
    def findOrder(self, numCourses: int, prerequisites: list[list[int]]) -> list[int]:
        g = {} # src -> dstlst
        indeg = Counter() # dst - num_indeg
        for edge in prerequisites:
            # [1,0]
            # To take course 1 you should have finished course 0.
            dst, src = edge
            if src in g:
                g[src].append(dst)
            else:
                g[src] = [dst]
            indeg[dst]+=1
        # print(g) # {0: [1]}
        # print(indeg) # Counter({1: 1})
        path = []
        q = deque()
        # start from 0 indeg and is valid source
        for course in range(numCourses):
            if course not in indeg and course not in g: # isolate node
                path.append(course)
            if course not in indeg and course in g: # valid start
                q.append(course)
        # print(visited)
        # the input do not say that we do not have graph
        # [[1,0],[1,2],[0,1]] => invalid
        # print(g) #{0: [1], 2: [1], 1: [0]}

        while q:
            q_len = len(q)
            for _ in range(q_len):
                cur_node = q.popleft()
                path.append(cur_node)
                if cur_node in g:
                    for next_node in g[cur_node]:
                        indeg[next_node]-=1
                        if indeg[next_node]==0:
                            q.append(next_node)
        # 看path有没有收齐
        return path if len(path) == numCourses else []


