class Solution:
    def countComponents(self, n: int, edges: list[list[int]]) -> int:
        # list of set?
        res = []
        # [[0,1],[2,3],[1,2]]
        # merge interval like, sort from start
        edges.sort()

        for edge in edges:
            in_exist=False
            for idx,group in enumerate(res):
                if edge[0] in group:
                    res[idx].add(edge[1])
                    in_exist=True
                if edge[1] in group:
                    res[idx].add(edge[0])
                    in_exist=True
            if not in_exist:
                st = set(edge)
                res.append(st)
        # print(res)
        for num in range(n):
            in_exist=False
            for idx,group in enumerate(res):
                if num in group:
                    in_exist=True
            if not in_exist:
                st = set([num])
                res.append(st)
        # print(res)
        return len(res)
