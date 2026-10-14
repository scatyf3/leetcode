# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def flatten(self, root: TreeNode | None) -> None:
        """
        Do not return anything, modify root in-place instead.
        preorder - root - left - right
        """

        def dfs(node):
            if node is None:
                return None, None
            left_start,left_end = dfs(node.left)
            right_start,right_end = dfs(node.right)
            node.left = None # remove left，防止递归遍历
            # error: 右指针串成的链表本身是对的，但每个节点原来的左孩子还挂着
            if left_start is None and right_start is None:
                return node,node
            elif left_start is None:
                node.right=right_start
                return node,right_end
            elif right_start is None:
                node.right=left_start
                return node,left_end
            else:
                node.right=left_start
                left_end.right=right_start
                return node,right_end
        res,_ = dfs(root)
        return res