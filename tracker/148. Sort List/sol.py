class Solution:
    def sortList(self, head: ListNode | None) -> ListNode | None:
        # 1. 递归出口：空链表或只有一个节点，本身就是有序的
        if head is None or head.next is None:
            return head

        # 2. 快慢指针找中点（fast 从 head.next 出发）
        slow, fast = head, head.next
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next

        # 3. 从中点切成两半
        mid = slow.next # error
        slow.next = None

        # 4. 两半分别排序
        left = self.sortList(head)
        right = self.sortList(mid)

        # 5. 合并两个有序链表（21. Merge Two Sorted Lists）
        dummy = ListNode(0)
        cur = dummy
        while left and right:
            if left.val<right.val:
                cur.next = left
                left = left.next
            else:
                cur.next = right
                right = right.next
            cur = cur.next
        cur.next = left if left else right   # 把剩下没合并完的一段接上去 # error
        return dummy.next


        