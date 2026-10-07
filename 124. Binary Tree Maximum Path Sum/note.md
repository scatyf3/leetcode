# 124. Binary Tree Maximum Path Sum

1. 对每个node调用dfs
2. dfs递归找最大left path和right path

agent：不用，dfs传max，然后nonlocal update max path即可

这里语义比较麻烦，path可以随便构造，1. 不需要经过root 2. 不需要leaf to leaf，所以dfs的递推麻烦