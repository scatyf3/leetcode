# 235. Lowest Common Ancestor of a Binary Search Tree

这里的key insight是利用binary tree的性质( assume p<q)
1. 如果p<r<q，则当前就是要找的
2. 如果p<q<r，往左找
3. 如果r<p<q，往右




有些奇怪的bug

```python
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':

        def dfs(p,q,node):
            if node.val>=p and node.val<=q:
                return node
            elif node.val>=p and node.val>=q: #left
                return dfs(p,q,node.left)
            elif node.val<=q and node.val<=p:
                return dfs(p,q,node.right)
            else:
                print("invalid")
                return node
```

如果里面递归的node写成root，会在大部分case上原地打转...dfs要不写外面，防止这种silence error