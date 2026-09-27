# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeElements(self, head: ListNode | None, val: int) -> ListNode | None:
        if head is None:
            return None
        cur = head
        guard = prev = ListNode()
        prev.next = cur
        while cur is not None:
            if cur.val==val:
                prev.next=cur.next
                cur=prev.next
            else:
                prev=prev.next
                cur=cur.next
        return guard.next
        