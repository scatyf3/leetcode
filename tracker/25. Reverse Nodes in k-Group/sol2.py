# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseKGroup(self, head: ListNode | None, k: int) -> ListNode | None:
        dummy = ListNode()
        dummy.next = head

        prev = dummy
        first = head
        if k==1:
            return head

        while True:
            end = prev # k step from prev, like dummy node do in remove k node
            for _ in range(k):
                if end:
                    end = end.next
            if not end: #tail group do not reverse
                # dummy is point to end of first group instead of real head...
                return dummy.next

            nxt = end.next
            # prev -> first -> end -> nxt
            prev_iter = first
            curr = first.next
            while curr is not nxt: # reverse end, need to judge current not nxt
                nxt_iter = curr.next
                curr.next = prev_iter
                prev_iter = curr
                curr = nxt_iter
            # prev -> first <- end x nxt
            prev.next=end
            first.next=nxt
            # prev -> end -> first -> nxt
            # iterate
            # prev -> end -> first -> nxt
            #  0   -> 0   ->  prev -> first
            prev = first
            first = nxt
        

            

