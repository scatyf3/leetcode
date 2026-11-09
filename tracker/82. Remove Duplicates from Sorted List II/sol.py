# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicates(self, head: ListNode | None) -> ListNode | None:
        if head is None:
            return None
        # remove 1 dup is easy but remove all is tricky
        swr = head.next
        swl = head
        to_remove=set()
        prev= None
        while swr is not None:
            if swl.val==swr.val:
                to_remove.add(swr.val)
            swl=swl.next
            swr=swr.next
        dummy=ListNode()
        dummy.next=head
        prev=dummy
        curr=head
        while curr:
            if curr.val in to_remove:
                nxt=curr.next
                prev.next=nxt
                curr=nxt
            else:
                prev=curr
                curr=curr.next
        return dummy.next