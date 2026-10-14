# 236. Lowest Common Ancestor of a Binary Tree

有道binary search tree lca的followup，如果有binary性质，我们很简单就能通过大小判断左侧有无p，右侧有无q，然后决定往哪里递归。

但是这里没有那么ez的性质，我们只能先递归到底下，然后把两个branch已知的信息递归返回，在当前node里看两遍递归返回的东西，返回有无p和有无q的bool

枚举好傻，但是没办法了，以及其实可以不枚举leaf（