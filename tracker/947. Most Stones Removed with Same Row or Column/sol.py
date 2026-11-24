class UF:
    def __init__(self):
        # forest
        self.parent = {}
        self.count = 0

    def find(self, x): # given an x, find it's root
        if x not in self.parent:
            self.parent[x] = x
            self.count += 1
        while self.parent[x] != x:
            # zip the path
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b): # test is connected or not
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.parent[ra] = rb
        self.count -= 1
        return True


class Solution:
    def removeStones(self, stones: list[list[int]]) -> int:
        uf = UF()
        for x, y in stones:
            uf.union(x, ~y)          # 行节点是 x，列节点是 ~y（负数，不会和行撞）
        return len(stones) - uf.count