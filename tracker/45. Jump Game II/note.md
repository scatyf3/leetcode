# 45. Jump Game II

这里是O(mn)，但agent老师说可以再压缩复杂度，即
对一个reachable，我们只care他能跳最远的地方？这样如何保障一定cover答案呢
1. dp是单调的
2. 我们只care 步数而不care路径

可以写成一个按层的bfs，很神奇