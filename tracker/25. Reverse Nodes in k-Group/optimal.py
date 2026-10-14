class Solution:
    def reverseKGroup(self, head: ListNode | None, k: int) -> ListNode | None:
        dummy = ListNode(0, head)
        group_prev = dummy                  # 上一组的尾巴
        while True:
            # 1. 走 k 步找这一组的最后一个节点; 不够 k 个就结束
            kth = group_prev
            for _ in range(k):
                kth = kth.next
                if not kth:
                    return dummy.next
            group_next = kth.next           # 先存: 反转时 kth.next 会被改掉

            # 2. 反转这一组; prev 初值 = 反转后尾巴该指向的节点
            prev, cur = group_next, group_prev.next
            while cur is not group_next:
                nxt = cur.next
                cur.next = prev
                prev, cur = cur, nxt

            # 3. 接回前面: 上一组尾巴 → 新头 kth; 旧头成了新尾巴
            old_head = group_prev.next
            group_prev.next = kth
            group_prev = old_head
