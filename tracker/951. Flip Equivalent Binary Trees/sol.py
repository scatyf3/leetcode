# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def flipEquiv(self, root1: TreeNode | None, root2: TreeNode | None) -> bool:
        # mirror => iterate in reverse order

        def dfs(node1,node2):
            if node1 is None and node2 is None:
                return True
            elif node1 is None and node2 is not None:
                #print(node1)
                #print(node2)
                return False
            elif node1 is not None and node2 is None:
                #print(node1)
                #print(node2)
                return False
            else:
                # reverse or non-reverse
                #print(node1.val==node2.val)
                # and默认优先级大于or
                return (node1.val==node2.val) and ((dfs(node1.left,node2.right) and dfs(node1.right,node2.left)) or (dfs(node1.right,node2.right) and dfs(node1.left,node2.left)))
        return dfs(root1,root2)
        