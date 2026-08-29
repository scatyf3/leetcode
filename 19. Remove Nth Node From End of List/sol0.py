# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        fast = head
        head_backup = head
        i = 0
        if n == 1:
            return None
        while fast.next is not None and i<n:
            fast = fast.next
            i+=1
        while fast.next is not None:
            fast = fast.next
            head = head.next
        head.next=head.next.next
        return head_backup