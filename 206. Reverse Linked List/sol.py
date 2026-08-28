# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        '''
        in place reverse
        return the new head (previous tail)
        '''
        def dfs(prev, curr):
            if curr is None:      # end of list, prev is the new head
                return prev
            nxt = curr.next       # save it, next line overwrites it
            curr.next = prev      # flip this one edge
            return dfs(curr, nxt) # pass the new head straight up
        return dfs(None, head)

        # iterative, no recursion depth limit
        # prev = None
        # while head:
        #     head.next, prev, head = prev, head, head.next
        # return prev
