传 depth，update maxdia：dfs 返回 `max(左 depth, 右 depth) + 1`，每个节点顺手 `maxdia = max(maxdia, 左 depth + 右 depth)`。

⚠ `nonlocal maxdia` 写在**要改它的那一层**（里层 dfs）里，不是在外层定义处 claim。
