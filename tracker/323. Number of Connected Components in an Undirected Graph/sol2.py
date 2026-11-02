class Solution:
    def countComponents(self, n: int, edges: list[list[int]]) -> int:
        # list size of n, 每个数值是它的parent，当value=index的时候是root，因为我们从这个状态开始
        # 不用list of set的原因是合并太恶心了，直接index
        parent = list(range(n))        

        def find(x):                   # 找 x 所在组的组长
            while parent[x] != x:
                parent[x] = parent[parent[x]]   # 路径压缩: 顺手把 x 挂到爷爷上
                x = parent[x]
            return x

        count = n                      # 一开始 n 组
        for a, b in edges:
            ra, rb = find(a), find(b)
            if ra != rb:               # 两头在不同组 -> 合并, 少一组
                parent[ra] = rb # set ra -> rb
                count -= 1
        return count
