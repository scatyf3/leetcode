# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        # sol1 的压缩版: is_leaf 那四个分支全删, 它们已经被 None 的 base case 覆盖
        # 叶子 vs 叶子     -> 走 else 也是 dfs(None,None) and dfs(None,None) and val==val
        # 叶子 vs 非叶子   -> 非叶子那侧至少一个孩子非空 -> dfs(None, 节点) -> False
        # 即"一空一非空"和"叶子对不上"是同一个 base case 在不同深度触发, 不是两种情况

        def dfs(p, q):
            if p is None and q is None:     # 两棵空树相同
                return True
            if p is None or q is None:      # 走到这说明至少一个非 None -> 一空一非空
                return False
            # val 放最前面: and 短路, 值不等立刻返回, 不用白跑整棵子树
            return p.val == q.val and dfs(p.left, q.left) and dfs(p.right, q.right)

        return dfs(p, q)

        # O(min(m,n)) 时间 —— 一旦不同就停, 不会跑完两棵树
        # O(min(m,n)) 空间 —— 递归栈深度 = 树高, 退化成链表时最坏 O(n)

        # 镜像 case: [1,2] vs [1,null,2] -> False
        # 这条划清了本题和 101 对称二叉树的界线: 同一套 dfs,
        # 区别只在递归时配对的是 left↔left 还是 left↔right
