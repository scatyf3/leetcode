# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        curA=headA
        curB=headB
        swapA=swapB=False
        while curA is not curB and curA and curB:
            if curA.next: 
                curA=curA.next
            elif not swapA:
                curA=headB
                swapA=True
            else:
                return None
            if curB.next:
                curB=curB.next
            elif not swapB:
                curB=headA
                swapB=True
            else:
                return None
        return curA