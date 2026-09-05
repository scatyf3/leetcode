
最naive的解法，用binary search插入有序数组，这样天然通过index好找median， insert O(logn), 访问想要的东西O(1)

这里需要注意的是二分搜索各种变体。

一个进阶的解法是用heap，一个存前半，另一个存后半？
0. 不需要全局有序
1. 把数据切成"较小的一半"和"较大的一半"
2. 较小那半里最大的是谁、较大那半里最小的是谁

ok，这里的思路是
1. 比较num和小堆和大堆的顶，insert到对应的半边
2. 然后rebalance两个堆
    1. 其实偷懒的做法是如果这玩意在中间，直接insert两次，这valid吗 => 不行，后面带来误差了
    2. 或者默认low可以比high多一个元素，如果奇数选low，偶数两者的顶


这里比insert的复杂度差在哪里
1. insert是n个O(logn)
2. 这个好像也是？

并非，insert是O(n)，其实search还行