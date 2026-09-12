class Solution:
    def goodNodes(self, root: TreeNode) -> int:
        '''
        a node X in the tree is named good if in the path from root to X there are no nodes with a value greater than X.
        '''
        max_count = 0
        def dfs(node,curr_max):
            nonlocal max_count
            if node is None:
                return
            if node.val>=curr_max:
                curr_max=node.val
                max_count+=1
            dfs(node.left,curr_max)
            dfs(node.right,curr_max)
        dfs(root,-1000000)
        return max_count