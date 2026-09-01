# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        def dfs(root):
            if(root is None):
                return True
            if(root.left is None and root.right is None):
                return True
            if(root.left is None):
                return root.val>root.right.val and dfs(root.right)
            if (root.right is None):
                return root.val>root.left.val and  dfs(root.left)
            if root.val>root.left.val and root.val>root.right.val:
                return dfs(root.right) and dfs(root.left)
            else:
                return False
        return dfs(root)


'''
Error
1. 右子树比较方向写反了: BST 是 左 < 根 < 右, 右孩子必须比根大,
   我写成了 root.val > root.right.val。连 [2,1,3] 都过不了 (2>1 ✓, 2>3 ✗)。
2. 更本质: 只比较了"节点 vs 它的直接孩子", 没有把祖先的约束往下传。
   BST 要求整棵子树落在一个区间里, 逐层局部比较发现不了隔代违规。
   反例 [5,1,4,null,null,3,6]:
        5
       / \
      1   4
         / \
        3   6
   局部看 4>3 ✓ 4<6 ✓, 但 3 和 4 都在 5 的右子树里却 < 5, 不是 BST。
3. 那一堆 root.left is None / root.right is None 的分支是白写的:
   上下界写法里递归到 None 直接 return True 就自然覆盖了叶子/单边情况。
   分支越多越容易在某一支里把符号写反 —— 错误 1 就是这么来的。
'''
