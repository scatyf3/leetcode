递归 `is_eq(a, b)` 判两棵子树互为镜像：都空为真、只一边空为假，否则 `a.val == b.val and is_eq(a.left, b.right) and is_eq(a.right, b.left)`；入口 `is_eq(root, root)`。

⚠ 二叉树节点不一定两个孩子都有，先处理「一边空一边不空」再取 `.val`。
