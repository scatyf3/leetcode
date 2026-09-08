# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        maxdia=0

        def dfs(node):
            nonlocal maxdia # 在这里claim访问一个nonlocal
            if node is None:
                return 0
            left_depth = dfs(node.left)
            right_depth = dfs(node.right)
            dia = left_depth+right_depth
            maxdia=max(maxdia,dia)
            return max(left_depth,right_depth)+1

        dfs(root)
        return maxdia


'''
diameter=left depth+right depth

传depth，update maxdia
'''