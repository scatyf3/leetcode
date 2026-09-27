# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicates(self, head: ListNode | None) -> ListNode | None:
        # sort
        # 0~300 num nodes
        if head is None:
            return None
        # at least 1
        prev = guard = ListNode(val=-114,next=head)
        cur = head
        while cur is not None:
            if prev.val==cur.val:
                # remove cur
                prev.next=cur.next
                cur=prev.next
            else:
                prev=prev.next
                cur=cur.next
        return guard.next
            