# 1043. Partition Array for Maximum Sum

1. dp存截止到当前index的最优解。
2. 对每个incoming元素，计算不同的分割，从0~k-1的segment被他cover