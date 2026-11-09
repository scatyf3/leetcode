# 852. Peak Index in a Mountain Array

binary search，但还是有问题不明

1. 比mid vs mid+1，因为mid向下取整，即在一些edge case里，mid会一路变成0，所以如果比mid和mid-1会越界，而mid+1永远安全
2. 在结束的时候，两个指针的shape时： r(peak-1) - l(peak), why. 定义上坡为t，下坡为f，peak的边界就是这样的