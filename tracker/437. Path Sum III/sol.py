# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def pathSum(self, root: TreeNode | None, targetSum: int) -> int:
        res = 0
        def dfs(node,val_need):
            nonlocal res
            if node is None:
                return 
            if val_need==node.val:
                # print(node.val) # -2? 3x2?
                res+=1
            dfs(node.left,val_need-node.val)
            dfs(node.right,val_need-node.val)
            dfs(node.left,targetSum) # 这里相当于不连续skip了
            dfs(node.right,targetSum)
        
        dfs(root,targetSum)
        return res


        