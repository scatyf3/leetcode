# 148. Sort List

标准的归并排序，但感觉对咋写完全不熟悉，思路没问题，让agent给个template填空...

## 踩坑

1. `mid = slow` → 应该是 `mid = slow.next`,**断开之前先存右半边的头**。写成 `slow` 的话右半边整段丢失,`slow` 同时出现在两半里,merge 时自己接自己成环
2. 收尾 `cur.next = right.next` → 应该是 `cur.next = left or right`。循环退出时至少一条已空,剩下那条整段有序,直接接上;`.next` 会跳过一个节点,而且 right 为 None 时直接炸
3. 找中点用 `fast = head.next`(落左中点),n=2 才切得开。见 [linked-list-template.md](../notes/linked-list-template.md) 第 1 节
