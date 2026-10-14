双重 DFS：外层遍历每个节点当起点，内层从起点往下传剩余值 `need - node.val`，`need == node.val` 就计数一次。

⚠ 「换起点」只能在外层做：在内层 dfs 里顺手 `dfs(child, targetSum)` 会让同一个起点被重启多次、重复计数（`1→1→1, target=1` 得 4 而不是 3）。路径必须连续，不能跳点。
