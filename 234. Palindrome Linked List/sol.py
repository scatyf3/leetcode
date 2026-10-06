# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def isPalindrome(self, head: ListNode | None) -> bool:
        # find mid (right)
        # than reverse - compare
        # or record?
        if head is None or head.next is None:
            return True
        slow = head
        fast = head.next
        while fast and fast.next:
            slow=slow.next
            fast=fast.next.next
        mid = slow.next
        slow.next=None
        # print(mid.val) # 2 in eg 1, not1
        # reverse the remain part
        dummy = ListNode()
        dummy.next=mid
        prev=None
        cur=mid
        while cur:
            nxt = cur.next
            cur.next=prev
            prev=cur
            cur=nxt
        # print(prev.val) # prev is new head
        prev_part_head = head
        last_part_head = prev
        #print(prev_part_head)
        #print(last_part_head)
        while prev_part_head and last_part_head:
            if prev_part_head.val!=last_part_head.val:
                return False
            prev_part_head=prev_part_head.next
            last_part_head=last_part_head.next
        #print(last_part_head)
        #print(prev_part_head)
        if prev_part_head and prev_part_head.next is None:
            return True
        elif last_part_head and last_part_head.next is None:
            return True
        elif prev_part_head is None and last_part_head is None:
            return True
        else:
            return False