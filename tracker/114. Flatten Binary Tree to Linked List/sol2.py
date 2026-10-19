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
                return None,None
            left_begin,left_end = dfs(node.left)
            right_begin,right_end = dfs(node.right)
            # print()
            node.left = None
            node.right = left_begin
            if left_end is not None:
                # print(left_end,right_begin)
                left_end.right = right_begin
            if left_begin is None and right_begin is not None:
                node.right = right_begin
            return node, right_end or left_end or node 
            # 不确定end是啥，一直返回right_end会导致丢信息

        root,end =  dfs(root)
        return root