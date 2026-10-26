class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        '''
        1. build graph according to prerequisites
        2. simulate bfs from start(0 indegree)
        prerequisites [0] -> [1]
        '''
        g = {} # start - end
        indeg = Counter() # node: cnt
        for p in prerequisites:
            if p[0] in g:
                g[p[0]].append(p[1])
            else:
                g[p[0]]=[p[1]]
            indeg[p[1]]+=1
        #print(g)
        #print(indeg)
        start = []
        for node in range(numCourses):
            if indeg[node]==0 and node in g: # do not care empty node
                start.append(node) #multi start
        # print(start)
        # print(start)
        q = deque(start)

        while q:
            q_len = len(q)
            for _ in range(q_len):
                cur_elem = q.popleft()
                if cur_elem in g:
                    next_list = g[cur_elem]
                    for next_elem in next_list:
                        indeg[next_elem]-=1
                        if indeg[next_elem]==0:
                            q.append(next_elem)
                # else, no next, just exit
        print(indeg)
        for key in indeg:
            if indeg[key]!=0:
                return False
        return True