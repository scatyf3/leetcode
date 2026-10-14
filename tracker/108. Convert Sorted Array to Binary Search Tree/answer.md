`dfs(left, right)` 取中点 `mid = (left + right) // 2` 当根，左子树建 `[left, mid-1]`、右子树建 `[mid+1, right]`，`left > right` 返回 None。
