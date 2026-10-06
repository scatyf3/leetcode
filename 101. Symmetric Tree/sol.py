# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isSymmetric(self, root: TreeNode | None) -> bool:
        # left.right = right.left
        # left.left = right.right
        def is_eq(left,right):
            if left is None and right is None:
                return True
            if left and right is None:
                return False
            if right and left is None:
                return False
            return left.val==right.val and is_eq(left.right,right.left) and is_eq(left.left, right.right)
        
        return is_eq(root,root)

        