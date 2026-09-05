# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        # 中序遍历法: BST 的中序序列必须严格递增。
        # 不用真的存下整个序列, 只留一个 prev。
        self.prev = float('-inf')

        def inorder(node):
            if node is None:
                return True
            if not inorder(node.left):
                return False
            if node.val <= self.prev:            # 严格递增, 相等也不行
                return False
            self.prev = node.val
            return inorder(node.right)

        return inorder(root)
