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

        解法: BFS  O(V+E) 时间 / O(V) 空间

        为什么 BFS 也行(而不是"BFS 不好搞依赖关系"):
        判据是"我的结果是不是子节点结果的函数"。
          克隆图  new.val = old.val          -> 与邻居无关, 无依赖
          树的深度 depth(u) = 1+max(子)      -> 有依赖, 必须后序 DFS
        这题无依赖, 所以遍历顺序完全不影响正确性 —— 把下面的 popleft() 换成 pop()
        就变成显式栈 DFS, 结果一模一样。
        '''
        if not node:
            return None

        visited = {node: Node(node.val)}      # ★ 起点在入队前就建好克隆
        q = deque([node])

        while q:
            old = q.popleft()                 # 换成 pop() 即为 DFS, 结果不变
            for nb in old.neighbors:
                if nb not in visited:
                    visited[nb] = Node(nb.val)    # ★ 发现即建, 不能拖到出队
                    q.append(nb)
                # 连边: 此刻两端的克隆都保证存在
                visited[old].neighbors.append(visited[nb])

        return visited[node]

        '''
        ★ 是 sol1 那个坑在 BFS 里的投影, 两者守同一条不变式:
          "一个节点的克隆体, 必须在任何人可能引用它之前就进 visited"

        如果严格改成"出队时才建克隆", 失败模式是 KeyError(不是死循环):
        执行到 visited[nb] 时邻居的克隆还不存在, 边无从连起 —— 当场炸, 不会被悄悄写错。
        想合法地推迟连边, 就得拆成两阶段, 见 sol3。

        与 sol1 的对应:
        |          | 递归 DFS              | BFS                     |
        | 何时建克隆 | 进入 dfs(old) 时建 old | 发现邻居、入队前建 nb    |
        | 何时连边   | 递归返回后 append     | 出队处理 old 时 append   |
        | 谁在切环   | if old in visited     | if nb not in visited    |

        Dry Run: 1 —— 2
          visited = {1: new1}, q = [1]
          出队 1: 邻居 2 不在 visited -> visited[2] = new2, 入队
                  new1.neighbors.append(new2)
          出队 2: 邻居 1 已在 visited -> 不入队
                  new2.neighbors.append(new1)
          q 空, 返回 new1

        Test Cases: 同 sol1。另: 3000 节点长链 sol1 爆栈, 本解通过。
        '''
