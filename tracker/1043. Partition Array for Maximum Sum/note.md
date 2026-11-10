# 1043. Partition Array for Maximum Sum

1. dp存截止到当前index的最优解。
2. 对每个incoming元素，计算不同的分割，从0~k-1的segment被他cover


这次终于推明白了，对每个元素，枚举subarray的划分，从1～k即可，indexing有点麻烦，但通过print之类的可以de明白