# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        '''
        这里的性质是binary search tree，感觉可以知道
        如果p<r<q，则当前就是要找的
        如果p<q<r，往左找
        如果r<p<q，往右
        assume p<q
        '''

        def dfs(p,q,node):
            if node.val>=p and node.val<=q:
                return node
            elif node.val>=p and node.val>=q: #left
                return dfs(p,q,node.left)
            elif node.val<=q and node.val<=p:
                return dfs(p,q,node.right)
            else:
                print("invalid")
                return node
            
        
        if p.val>q.val:
            tmp=p
            p=q
            q=tmp
        return dfs(p.val,q.val,root)