class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        idx_of = {v: i for i, v in enumerate(inorder)}  # 预处理 O(n)

        def dfs(pre_l, pre_r, in_l, in_r):  # 都是左闭右开
            if pre_l >= pre_r:
                return None
            root_val = preorder[pre_l]
            idx = idx_of[root_val]          # O(1) 找 root
            left_size = idx - in_l
            left = dfs(pre_l + 1, pre_l + 1 + left_size, in_l, idx)
            right = dfs(pre_l + 1 + left_size, pre_r, idx + 1, in_r)
            return TreeNode(root_val, left, right)

        return dfs(0, len(preorder), 0, len(inorder))