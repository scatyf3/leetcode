# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseKGroup(self, head: ListNode | None, k: int) -> ListNode | None:
        start = []
        end = []
        if k==1:
            return head # no need to reverse
        
        cnt = 0
        cur = head
        while cur:
            #print(cnt)
            #print(cnt%k)
            if cnt%k==0:
                start.append(cur)
            if cnt%k==k-1:
               end.append(cur)
            cur = cur.next
            cnt+=1
        #print(len(start))
        #print(len(end))
        assert len(start)==len(end) or len(start)==len(end)+1
        if cnt%k!=0: # 最后一组<k的不reverse
            remain_start = start.pop()
            # remain_end= start.pop()
        assert len(start)==len(end) 
        dummy = ListNode()
        dummy.next=head

        for i in range(len(start)):
            # reverse current
            prev = start[i]
            cur=start[i].next
            stop = end[i].next
            print(prev.val)
            while cur is not stop: #可能会被改
                print(cur.val)
                nxt = cur.next
                # reverse the link
                cur.next = prev
                # move forward
                prev = cur
                cur = nxt
        dummy.next=end[0]
        for i in range(1,len(end)):
            start[i-1].next=end[i] # start是tail，end是head
        if cnt%k!=0:
            start[len(end)-1].next=remain_start
        else:
            start[len(end)-1].next=None # 否则还有环

        return dummy.next   