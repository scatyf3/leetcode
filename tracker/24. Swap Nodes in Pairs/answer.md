dummy 接头，每轮把 `prev → cur → nxt → nxt_nxt` 改成 `prev → nxt → cur → nxt_nxt`：`prev.next = nxt`、`nxt.next = cur`、`cur.next = nxt_nxt`，循环条件 `cur and cur.next`。

⚠ 交换后 `cur` 成了这一对的尾巴，所以下一轮 `prev = cur`（不是 `nxt`），`cur = nxt_nxt`。和纯反转的 prev/cur 语义不一样。
