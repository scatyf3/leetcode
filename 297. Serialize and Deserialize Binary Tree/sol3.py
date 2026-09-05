# 纯函数版: 不用共享游标, 把"我吃到哪了"穿在返回值里往上报。
# sol.py  = 共享游标 (nonlocal i), sol2.py = 层序 BFS, 这里是第三种。
# 约定: build(start) 的第二个返回值 = 我这棵子树吃完之后的第一个下标。

# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Codec:
    def serialize(self, root):
        """:type root: TreeNode  :rtype: str"""
        res = []
        def dfs(node):
            if node is None:
                res.append('#')
                return
            res.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ','.join(res)

    def deserialize(self, data):
        """:type data: str  :rtype: TreeNode"""
        vals = data.split(',')          # 要按下标取, 所以是 list, 不能是 iter

        def build(start):
            """解析从 vals[start] 开始的那棵子树。
            返回 (子树的根, 这棵子树吃完之后的第一个下标)"""
            if vals[start] == '#':
                return None, start + 1                    # 空树只吃掉一格 '#'
            node = TreeNode(int(vals[start]))
            node.left,  right_start = build(start + 1)    # +1 = 跳过根自己那格
            node.right, subtree_end = build(right_start)  # 右子树紧接左子树的结束处
            return node, subtree_end

        root, _ = build(0)
        return root
