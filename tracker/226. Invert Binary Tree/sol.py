# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        # swap when only leaf is reached
        # another type of dfs, change it in place intead of recursive
        def dfs(node):
            if node is None:
                return
            # revert
            tmp = node.left
            node.left=node.right
            node.right=tmp
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return root # return root
