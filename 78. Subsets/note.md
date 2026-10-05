# 78. Subsets

有两种递归，一个是递归到底(leaf)才收集这个solution，另外一个就是每个中间状态都valid，这道题是后者

记得dfs时候idnex+1递推，否则死循环了