# 253. Meeting Rooms II

1. naive：迭代每个点，从1到max end
2. observation: overlap状态当且在start或者end端才改变
3. 迭代change point，然后save start和end两个counter，每个端点可能有多次跳变