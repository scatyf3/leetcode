class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        def dfs(p,q):
            if p is None and q is None:
                return True
            elif p is None:
                return False
            elif q is None:
                return False
            return dfs(p.left,q.left) and dfs(p.right,q.right) and p.val==q.val
        
        return dfs(p,q)
        