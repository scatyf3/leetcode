哈希表 `key → 节点` + 带头尾哨兵的双向链表（head 侧最新）：get / put 命中就把节点挪到 head 后面，超容量删 `tail.prev` 并 `del mp[node.key]`。

⚠ 摘下 / 插入要改两个方向四根指针，漏一根反向链就断；put 已存在的 key 只更新 val 再挪到头，不能新建节点。
