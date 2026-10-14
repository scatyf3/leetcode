# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        '''
        换框架:先序序列化成字符串,子树关系 -> 子串关系。只需要一个递归。
        O(m+n) (把 in 换成 KMP 可以保证线性)

        两个分隔细节,少一个就错:
          "#" 空节点占位  —— 否则 [1,2](2 是左孩子) 和 [1,null,2](2 是右孩子)
                             序列化成同一个串,结构信息丢失
          "^" 值前分隔符 —— 否则 root=[12], subRoot=[2] 会因为 "2" 是 "12" 的子串而误判
        '''
        def ser(node):
            if node is None:
                return "^#"
            return "^" + str(node.val) + ser(node.left) + ser(node.right)

        return ser(subRoot) in ser(root)


# 另一种等价写法:搜索层嵌套在里面,靠闭包看见完整的 subRoot。
# 和 sol.py 一样是两个递归 —— 说明关键不是"写在哪个作用域",
# 而是"必须有两个步进方式不同的递归",以及"每个候选点手上有完整的 subRoot"。
#
# class Solution:
#     def isSubtree(self, root, subRoot) -> bool:
#         def isSame(a, b):
#             if a is None or b is None:
#                 return a is None and b is None
#             return a.val == b.val and isSame(a.left, b.left) and isSame(a.right, b.right)
#         def search(node):
#             if node is None:
#                 return subRoot is None
#             return isSame(node, subRoot) or search(node.left) or search(node.right)
#         return search(root)
