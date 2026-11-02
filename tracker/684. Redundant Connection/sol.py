class Solution:
    def findRedundantConnection(self, edges: list[list[int]]) -> list[int]:
        n = len(edges)                 # 树 + 1 条边 -> 点数 == 边数
        parent = list(range(n + 1))    # 点是 1..n, 下标 0 空着

        def find(x):
            while x!=parent[x]:
                x=parent[x]
            return x

        for a, b in edges:             # 按输入顺序加边
            ra, rb = find(a), find(b)
            if ra==rb:                    # TODO 2: 什么条件说明这条边成环?
                return [a,b]             # TODO 3: 返回什么?
            # TODO 4: 不成环 -> 合并两组 (挂 root 还是挂端点?)
            parent[rb]=ra


        return [] # 题目保证一定有答案, 走不到这里
