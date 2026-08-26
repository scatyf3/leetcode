from collections import deque

"""
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
"""


class Solution:
    def cloneGraph(self, node: 'Node') -> 'Node':
        '''
        Input / Target / Return / Output: 同 sol1

        解法: 两阶段 BFS —— 先把所有点建出来, 再统一连边
              O(V+E) 时间 / O(V) 空间, 只是多遍历一趟(常数)

        这版的价值不在性能, 在于它把"这题无依赖"这件事变成了代码结构:
        阶段1 和阶段2 都不需要任何顺序保证。
        代价换来的是 sol1/sol2 里那个 ★ 时机问题彻底消失 ——
        阶段2 开始时所有克隆都已存在, 不可能查不到, 也就没得写错。
        新手写这题反复踩"什么时候建、什么时候连", 直接用这版可以绕开。
        '''
        if not node:
            return None

        # ---- 阶段 1: 只建点, 一条边都不连 ----
        visited = {node: Node(node.val)}
        q = deque([node])
        while q:
            old = q.popleft()
            for nb in old.neighbors:
                if nb not in visited:
                    visited[nb] = Node(nb.val)
                    q.append(nb)

        # ---- 阶段 2: 点全在了, 连边毫无顺序要求 ----
        for old, new in visited.items():
            new.neighbors = [visited[nb] for nb in old.neighbors]

        return visited[node]

        '''
        注意阶段2 用的是赋值 new.neighbors = [...] 而不是 append:
        阶段1 建出来的壳 neighbors 本来就是空的, 直接整体赋值更干净;
        若改成 append 也对, 但重复跑两次就会把边加两遍(调试时容易踩)。

        为什么可以这么拆 —— "先占位后填充"的最纯粹形态:
        Node 是可变对象, 阶段1 拿到的是一堆合法但内容为空的地址,
        别人引用它们完全没问题, 内容什么时候填都行。
        反过来说, 如果 Node 是不可变的(比如 namedtuple/frozen dataclass),
        这题就真的无解了 —— 环意味着 u 和 v 互相需要对方已构造完成。

        Dry Run: 1 —— 2
          阶段1: visited = {1: new1, 2: new2}, 两个壳的 neighbors 都是 []
          阶段2: new1.neighbors = [new2];  new2.neighbors = [new1]
          返回 new1

        Test Cases: 同 sol1。300 组随机连通图 + 3000 长链均通过。
        '''
