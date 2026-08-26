# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        # dfs(tree_1, tree_2), return true/false while the subtree is same
        # when to return
        # empty => true
        # difference value or branching => false
        # edge case
 
        
        def is_leaf(node):
            return node.left is None and node.right is None
        
        def dfs(p,q):
            if p is None and q is None:
                return True
            elif p is None:
                return False
            elif q is None:
                return False

            if is_leaf(p) and is_leaf(q) and p.val==q.val:
                return True
            if is_leaf(p) and is_leaf(q) and p.val!=q.val:
                return False
            if is_leaf(p) and not is_leaf(q):
                return False
            if not is_leaf(p) and is_leaf(q):
                return False
           
            else:
                return dfs(p.right,q.right) and dfs(p.left,q.left) and p.val==q.val
        return dfs(p,q)

'''
1. 记得比每个迭代过的节点 
2. 一些edgecase和搜索优化
'''
