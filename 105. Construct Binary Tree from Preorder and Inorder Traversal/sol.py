# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        def dfs(preorder,inorder,pre_l,pre_r,in_l,in_r):
            if pre_l==pre_r:
                return
            if in_l==in_r:
                return
            cur_root_val=preorder[pre_l]
            cur_node=TreeNode(cur_root_val,None,None)
            r_start_idx=-1
            for i in range(in_l,in_r):
                if inorder[i]==cur_root_val:
                    # L[in_l,i-1] i R[i+1,in_l+in_len]
                    # in range [in_l,i), [i+1,in_r)
                    r_start_idx = i+1
                    break                                         # <<< 1. 找到就停
            if r_start_idx==-1:
                print("invalid, not found")
            left_len = r_start_idx-1-in_l                          # <<< 2. 先算左子树长度
            left_node  = dfs(preorder,inorder,pre_l+1,          pre_l+1+left_len, in_l,          r_start_idx-1)  # <<< 3
            right_node = dfs(preorder,inorder,pre_l+1+left_len, pre_r,            r_start_idx,   in_r)           # <<< 3
            cur_node.left=left_node
            cur_node.right=right_node
            return cur_node
        root=dfs(preorder,inorder,0,len(preorder),0,len(inorder))
        return root



'''
preorder = [3,9,20,15,7], 
inorder = [9,3,15,20,7]
1.  node=2, find 3 in inorder
2. inorder: left:[9],right [15,20,7] preorder: [9],[15,20,7]

所以right其实不天然align

'''



'''
pre: root-left-right
inorder:left-root-right

pre_l_start,pre_len
in_l_start,in_len
'''