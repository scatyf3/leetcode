"""
# LeetCode 给的节点定义(实际提交时它在注释里, 不用自己写):
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
"""


class Solution:
    def cloneGraph(self, node: 'Node') -> 'Node':
        '''
        Input:
        - node: Node, 无向连通图中的任意一个节点(题目保证从它能到达所有节点)
                0 <= n <= 100, 无重边无自环, val 互不相同且等于节点下标+1
        Target: 深拷贝整张图
        Return: 克隆图中"对应于入参 node"的那个节点
                —— 图没有容器对象, 一个节点引用就是整张图的句柄(靠连通性保证)
                —— 必须是对应节点: 判题从原图 node 和你的返回值同步 BFS 比对
        Output: Node (或 None)

        解法: 递归 DFS  O(V+E) 时间 / O(V) 空间(visited + 递归栈)

        核心难点不是"拷贝", 是"环":
        无向图每条边存两次(u 在 v.neighbors 里, v 也在 u.neighbors 里),
        所以任意一条边本身就是环 -> 依赖关系是循环的 -> "先算依赖再算我"根本不成立。
        破法: 先占位后填充。Node 是可变对象, 先建好空壳拿到地址, 边回头再填。
        '''
        if not node:
            return None                       # 空图

        visited = {}                          # 原节点 -> 克隆节点
                                              # 一张表两个职责: ① 切环 ② 查"某原节点的克隆是谁"
                                              # 只用 set 会卡在职责②: 知道 u 访问过, 却拿不到它的克隆去连边

        def dfs(old: 'Node') -> 'Node':
            '''
            「查表；查不到就现建一个壳登记进去，再递归把内容填上」
            如果查到是啥意思

            '''
            # 已经被visit，立刻返回那个已有的克隆，不建新对象、也不再往下递归
            if old in visited:
                return visited[old]           # 环的出口 + 复用已建好的克隆

            # 如果没被visit，clone+加到表格里
            new = Node(old.val)               # 只用 val 就能建, 不依赖任何邻居
            visited[old] = new                # ★ 必须在递归邻居之前登记!
            
            # 启动下一步
            for nb in old.neighbors:
                new.neighbors.append(dfs(nb)) # 环上返回的可能是 neighbors 还空着的半成品,
                                              # 但我们只需要它的地址, 内容由它自己的那层填
            return new

        return dfs(node)

        '''
        ★ 的顺序是全题唯一的坑。放到 for 之后:
          dfs(1) -> dfs(2) -> dfs(1), 此时 visited 仍是空的 -> 又新建一个 Node(1) -> 无限递归

        Dry Run: 最简单的一条边 1 —— 2
          dfs(1): visited 无 1 -> new1 = Node(1); visited[1] = new1     ★
                  遍历 1 的邻居 [2]:
                    dfs(2): visited 无 2 -> new2 = Node(2); visited[2] = new2   ★
                            遍历 2 的邻居 [1]:
                              dfs(1): 已在 visited -> 返回 new1   <- 环在这里被切断
                            new2.neighbors = [new1]      (此刻 new1.neighbors 还是空的, 没关系)
                  new1.neighbors = [new2]
          返回 new1

        Test Cases:
        None            -> None          空图
        单节点无边       -> 单节点无边
        自环 u->u        -> 克隆的自环(不能指回原图)
        1-2, 1-3, 2-4, 3-4  (LC 官方样例, 有环)
        长链 (压力测试)   -> 递归深度 = 图的直径; n=3000 时 RecursionError
                            LC 约束 n<=100 所以安全, 想稳妥见 sol2/sol3

        验证标准(判题程序做的三件事):
        1. 结构同构  2. val 相同  3. 没有任何引用指回原图 <- 第3条才是"深拷贝"的实际含义
        '''
