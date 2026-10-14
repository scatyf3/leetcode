class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        graph = [[] for _ in range(numCourses)]   # graph[u] = 修完 u 以后会解锁哪些课
        indeg = [0] * numCourses

        for a, b in prerequisites:
            graph[b].append(a)                                   # 坑1: 建边, 谁指向谁 ([a,b] = 先修 b)
            indeg[a]+=1                                   # 坑2: 谁的入度 +1

        q = deque([i for i in range(len(indeg)) if indeg[i]==0]) # 坑3: 起点是哪些课 (多源)
        taken = 0

        while q:
            u = q.popleft()
            taken+=1                                   # 坑4: 修完一门, 记一下
            for v in graph[u]:
                indeg[v]-=1                               # 坑5: 修完 u 以后 v 的入度怎么变
                if indeg[v]==0:                           # 坑6: 什么时候 v 可以入队
                    q.append(v)

        return taken==numCourses                              # 坑7: 怎么判断修完了没有 (对照例 2)
