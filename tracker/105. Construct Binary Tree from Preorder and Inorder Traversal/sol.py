class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        def dfs(preorder,inorder,pre_l,pre_r,in_l,in_r): 
            if pre_r-pre_l<=0:
                return None
            # 都是左开右闭
            # 从preorder拿到root
            # print("rootval",pre_l)
            root_val = preorder[pre_l]
            # 从root切分左右
            in_ll = in_l
            in_rr = in_r
            num_left_tree = 0
            in_lr = 0
            in_rl = 0
            for idx in range(in_l,in_r):
                num_left_tree+=1
                if inorder[idx]==root_val:
                    in_lr = idx
                    in_rl = idx+1
                    break # 找到就break，否则num_left_tree invalid
            pre_ll = pre_l+1
            pre_rr = pre_r
            pre_lr = pre_l+num_left_tree
            pre_rl= pre_l+num_left_tree
            left_node = dfs(preorder,inorder,pre_ll,pre_lr,in_ll,in_lr)
            right_node = dfs(preorder,inorder,pre_rl,pre_rr,in_rl,in_rr)
            root_node = TreeNode(root_val,left_node,right_node)
            return root_node
        root = dfs(preorder,inorder,0,len(preorder),0,len(inorder))
        return root
