class Solution:
    def oddEvenList(self, head: ListNode | None) -> ListNode | None:
        odd_head = odd_iter = ListNode()
        even_head = even_iter = ListNode()
        curr=head
        cnt=0
        while curr:
            nxt=curr.next
            if cnt%2==0:
                odd_iter.next=curr
                odd_iter=odd_iter.next
            else:
                even_iter.next=curr
                even_iter=even_iter.next
            curr.next=None
            cnt+=1
            curr=nxt
        #print(odd_head)
        #print(even_head)
        odd_iter.next=even_head.next
        return odd_head.next