# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        # 上下界法: 每个节点必须落在 (low, high) 开区间里,
        def dfs(node, low, high):
            if node is None:
                return True                      # base case 顺带覆盖了叶子和单边孩子
            if not (low < node.val < high):
                return False
            # 左子树，用root val update上界，柚子树用root val update下界
            return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)

        return dfs(root, float('-inf'), float('inf')) # place holder
