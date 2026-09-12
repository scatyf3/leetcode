class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        '''
        hint:BST 的哪种遍历顺序，得到的序列刚好是从小到大排好的？98 的 sol2.py 已经用过这个性质。
        left-root-right
        return the array and index by k
        '''
        saved=[]
        def dfs(node):
            if node is None:
                return
            dfs(node.left)
            saved.append(node.val)
            dfs(node.right)
        dfs(root)
        
        return saved[k-1]