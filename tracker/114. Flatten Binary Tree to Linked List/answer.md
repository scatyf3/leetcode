后序 dfs 返回拉平后的 `(head, tail)`，拼成 `node → 左链 → 右链`：`node.right = left_head`、`left_tail.right = right_head`，返回 `(node, 最后一段非空的 tail)`。

⚠ 要 `node.left = None`：右指针串对了，但原来的左孩子还挂着就不算链表（踩过）。
