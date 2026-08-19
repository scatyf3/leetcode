记忆化遍历，有点类似之前模拟那道题

1. naive解是双循环，记忆化解建hash table（当然不用explitcit hash，set+数值关系就行）+ 入口剪枝
2. 第一轮找start，之前的那个是要找唯一start，现在的是要找全部valid的start。当然模拟那道题如果有多start很显然不valid
3. 遍历start，用set查找长度，直接max 链路长度即可

如果不入口剪枝只建hash是不是也是o(n)

不是，只建 hash 是 O(n²)。这两个优化是正交的：

hash 让每一"步"从 O(n)（线性扫数组）降到 O(1)
入口剪枝 让总"步数"从 O(n²) 降到 O(n)

无hash无数组剪枝是O(n^3)

for each start
    find path(o(n^2))

1. 不剪枝的版本复杂度是数据相关的，O(n²) 只是它的上界（最坏情况）
2. 复杂度记号默认说的就是最坏情况上界，所以 note 里标 O(n²) 是对的