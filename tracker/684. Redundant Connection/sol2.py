class Solution:
    def findRedundantConnection(self, edges: list[list[int]]) -> list[int]:
        n = len(edges)                 # 树 + 1 条边 -> 点数 == 边数
        parent = list(range(n + 1))    # 点是 1..n, 下标 0 空着

        def find(idx,parent):
            while idx!=parent[idx]:
                idx=parent[idx]
            return idx

        # iterate through edges
        for edge in edges:
            src,dst=edge
            root_src=find(src,parent)
            root_dst=find(dst,parent)
            if root_src==root_dst:
                # already linked, can be remove
                return edge
            else:
                parent[root_dst]=root_src # 只操作root，不操作dst/src本体
        