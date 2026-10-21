# 1043. Partition Array for Maximum Sum

我：heap找topk，然后划分各自的range

agent：问题是最大值无法局部决定。dp，里面存划分后的最大值，对每个positoin，枚举其可能长度，update dp