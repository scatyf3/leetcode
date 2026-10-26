"""
# Definition for a Node.
class Node:
    def __init__(self, val: int = 0, left: 'Node' = None, right: 'Node' = None, next: 'Node' = None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
"""

class Solution:
    def connect(self, root: 'Node') -> 'Node':
        # next is go to next layer
        if root is None:
            return
        q = deque([root])
        while q:
            q_len = len(q)
            prev = q.popleft()
            if prev.left: # append none will cause issue
                q.append(prev.left)
            if prev.right:
                q.append(prev.right)
            for i in range(q_len-1):
                curr = q.popleft()
                if curr.left:
                    q.append(curr.left)
                if curr.right:
                    q.append(curr.right)
                prev.next=curr
                prev = curr #update prev
                # print(prev.val,curr.val)
        return root

        