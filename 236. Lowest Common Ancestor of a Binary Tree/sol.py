class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        '''
        我们想要的是一个node在左，一个node在右

        但之前是binary search，现在只是普通的tree，没啥关系

        先一直递归，然后返回的是左边元素和右边元素的set呗

        agent：不需要set，直接返回有p或者有q
        '''
        lca_node=None
        def dfs(node):
            nonlocal lca_node
            if node is None:
                return False, False
            left_has_p,left_has_q = dfs(node.left)
            right_has_p,right_has_q = dfs(node.right)
            if (node is p or left_has_p) and (node is q or right_has_q) :
                lca_node=node
            if (node is q or left_has_q) and (node is p or right_has_p):
                lca_node=node

            return (node is p or left_has_p or right_has_p), (node is q or left_has_q or right_has_q)
        dfs(root)
        return lca_node