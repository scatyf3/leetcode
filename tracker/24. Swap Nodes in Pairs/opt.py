class Solution:

    def swapPairs(self, head):
        def _swap(head,tail):
            tail.next=head
            return tail,head
        
        if head is None or head.next is None:
            return head
        
        guard = prev_tail = ListNode()
        prev_tail.next=head
        first = head
        second = head.next

        while first is not None and second is not None:
            next_first=second.next
            new_first,new_second = _swap(first,second)
            prev_tail.next=new_first
            new_second.next=next_first
            prev_tail = new_second
            first = next_first
            if next_first:
                second = next_first.next
        return guard.next