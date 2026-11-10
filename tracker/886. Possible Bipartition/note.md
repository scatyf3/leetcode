# 886. Possible Bipartition


你的直觉是对的，但是不好写成程序，我们用模拟染色。

1. 迭代图节点，每个节点bfs染1/-1，临近的节点不能相通
2. 如果check出相同，立刻返回false，否则都迭代完，返回true