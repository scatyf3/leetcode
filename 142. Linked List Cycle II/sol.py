# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # return the node where the cycle begins
        if head is None:
            return None
        if head.next!=None:
            fast = head.next.next
            slow = head.next
        else:
            return None

        while fast !=slow:
            slow=slow.next
            if fast!=None and fast.next!=None:
                fast=fast.next.next
            else: 
                return None
        slow = head
        while fast !=slow:
            slow=slow.next
            fast=fast.next

        return slow