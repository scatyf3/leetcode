# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseKGroup(self, head: ListNode | None, k: int) -> ListNode | None:
        dummy = ListNode()
        dummy.next=head
        prev = dummy
        first=head
        end = first
        nxt = None
        while True:
            cnt=0
            for _ in range(k):
                if end:
                    end=end.next
                    cnt+=1
            if cnt!=k: # tail case, do not reverse
                break
            nxt=end
            prev_iter = prev
            curr=first
            #print(curr)
            #print(end)
            # print("curr state",prev.value,first.value,end.value,nxt.value)
            while curr!=end:
                # save
                nxt_iter=curr.next
                # swap
                curr.next=prev_iter
                # print("swap",curr.val,prev_iter.val)
                # iterate
                prev_iter=curr
                curr=nxt_iter
                
            # update connection
            prev.next = prev_iter # update prev to current new head
            first.next=nxt # update new tail to nxt
            # print(dummy.next)
            # iterate
            prev=first
            first=prev.next

        return dummy.next

