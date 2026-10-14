哨兵 `guard.next = head`，`prev` / `cur` 同步走：`cur.val == val` 时 `prev.next = cur.next; cur = prev.next`，prev 不动；否则两者各前进一步；返回 `guard.next`。

⚠ 删除后是 `cur = prev.next`，写成 `cur = prev.next.next` 会一次走两步，漏判下一个节点。
