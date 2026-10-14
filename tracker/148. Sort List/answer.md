归并排序：快慢指针 `slow, fast = head, head.next` 找左中点，`mid = slow.next; slow.next = None` 切两半，分别递归排序，再用 dummy 合并，收尾 `cur.next = left or right` 整段接上。

⚠ 断开前先存 `mid = slow.next`（写成 `slow` 会丢节点/成环）；fast 从 `head.next` 出发，n = 2 才切得开。
