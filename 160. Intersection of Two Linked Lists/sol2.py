# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        # 走完自己再走对方: 两人都走 a+b(+c) 步, 必在交点或 None 处相遇
        curA, curB = headA, headB
        while curA is not curB:
            curA = curA.next if curA else headB
            curB = curB.next if curB else headA
        return curA
