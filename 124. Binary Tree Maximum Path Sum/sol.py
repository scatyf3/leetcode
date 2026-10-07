# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maxPathSum(self, root: TreeNode | None) -> int:
        max_sum=float("-inf")

        def dfs(node):
            nonlocal max_sum
            if node is None:
                return 0
            
            left_max=dfs(node.left)
            right_max=dfs(node.right)
            cur_max_path=max(left_max+node.val+right_max,node.val+left_max,node.val+right_max,node.val)
            # 不用完整的path，一个node也行吗
            if cur_max_path>max_sum:
                max_sum=cur_max_path
            return max(max(left_max,right_max)+node.val,node.val) # 可以不要分支的max，只要自己的val
        dfs(root)
        return max_sum
