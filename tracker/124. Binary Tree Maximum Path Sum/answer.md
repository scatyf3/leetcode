后序 DFS，`dfs(node)` 返回**以 node 为顶、只往一侧向下**的最大和 `max(val, val + max(L, R))`；在每个节点用拐弯路径 `max(val, val+L, val+R, val+L+R)` 更新 nonlocal `max_sum`。

⚠ 交给父亲的只能是单边，拐过弯的路径不能再往上接；`max_sum` 初值 `-inf`（全负树）。
