class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        jw=0
        head = res = ListNode() 
        while l1 is not None or l2 is not None or jw>0:
            if l1 is not None and l2 is not None:
                val = l1.val+l2.val+jw
                l1=l1.next
                l2=l2.next
            elif  l1 is not None:
                val = l1.val+jw
                l1=l1.next
            elif l2 is not None:
                val = l2.val+jw
                l2=l2.next
            else:
                val=jw
            jw = val//10
            new_node=ListNode(val%10,None)
            res.next=new_node
            res=res.next

        return head.next