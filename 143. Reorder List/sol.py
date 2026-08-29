# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        """
        Do not return anything, modify head in-place instead.
        1. split to previous half and second half
        2. reverse second half
        3. merge 2 linkedlist
        """
        # split
        fast = slow = head
        if head is None:
            return

        while fast.next is not None and fast.next.next is not None:
            slow = slow.next
            fast = fast.next.next
        # 1,2,3,4 -> s=2, f=3 ; 1,2,3 -> s=2, f=3
        # fast 只是配速器, 用完就丢: 它停在末尾附近, 不是后半段的头
        # slow 停在前半段最后一个节点, 所以后半段的头永远是 slow.next
        # 前半段长度 >= 后半段长度 (奇数时多 1, 偶数时相等)

        # disconnect
        # reverse 会把原 slow.next 的 next 置为 None, 两半此时已断开;
        # slow.next=None 是把 slow 这一侧的指针也清干净, 两句顺序无所谓
        head_second_half = self.reverse(slow.next)
        slow.next = None
        self.merge_to(head, head_second_half)

    def reverse(self, head):
        prev, curr = None, head
        while curr is not None:  # 条件是 curr 不是 curr.next, 否则最后一条边不翻
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        return prev  # 返回 prev 不是 curr, curr 此刻已经是 None

    def merge_to(self, first, second):
        '''
        merge
        1,2
        4,3
        to
        1,4,2,3
        '''
        if second is None:
            return
        if first.next is None:
            first.next = second
            return
        prev = first
        curr = first.next
        node_to_insert = second
        while node_to_insert is not None:
            prev.next = node_to_insert
            next_insert = node_to_insert.next
            node_to_insert.next = curr
            node_to_insert = next_insert
            prev = curr
            # 偶数长度时两半等长, 最后一轮 curr 已经是 None, 必须挡一下
            curr = curr.next if curr is not None else None

        '''
        Dry Run (n=5):
            split : 1->2->3 | 4->5
            rev   : 1->2->3 | 5->4
            merge : 1->5->2->4->3
        Test Cases: n = 0,1,2,3,4,5,6,7  全部验过 (见 note.md 的对拍)
        '''
