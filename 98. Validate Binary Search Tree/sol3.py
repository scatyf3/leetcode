# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        # 自底向上: 参数什么都不传, 全靠返回值把"子树极值"往上带。
        # 判定条件直译自定义: 左子树max < root < 右子树min。
        # 返回 (子树是否合法, 子树最小值, 子树最大值)
        def dfs(node):
            if node is None:
                # 空子树的哨兵故意反着填: min=+inf, max=-inf
                # 这样 lmax < node.val 和 node.val < rmin 在缺孩子时自动成立, 不用特判
                return True, float('inf'), float('-inf')

            lok, lmin, lmax = dfs(node.left)
            rok, rmin, rmax = dfs(node.right)
            # 注意: 这里不能像 sol.py 那样 and 短路,
            # 两边都必须递归完才拿得到极值 —— 这是自底向上的固有代价
            ok = lok and rok and lmax < node.val < rmin

            # 三方取极值, 无条件是这棵子树真正的 min/max。
            # (只写 min(lmin, node.val) 也能过, 但那依赖"已经合法"这个前提,
            #  非法时返回的极值是错的 —— 反正 ok 已经 False 了才没出事。别写那种。)
            return ok, min(lmin, rmin, node.val), max(lmax, rmax, node.val)

        return dfs(root)[0]


'''
和另外两版的关系 —— 同一个约束的三个流向:

    sol.py   自顶向下   参数带祖先区间 (low, high)   返回 bool      可短路
    sol2.py  横向       self.prev 沿中序序列         返回 bool      可短路
    sol3.py  自底向上   无参数                       返回 (ok,min,max)  不可短路

面试默认写 sol.py。sol3 的存在价值是: 当题目要"从下往上聚合"时只有这个方向能用,
比如 LC 333 最大 BST 子树 —— 那题要顺带把子树 size 一起返回上来。
'''
