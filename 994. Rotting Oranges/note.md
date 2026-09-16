# 994. Rotting Oranges

1. 感觉更接近模拟+层序遍历，collect全部腐烂的橘子起点，然后per step模拟即可
2. 还是之前说的for _ in len(q) 省去俩队列


说起来我们前面做过的grid题可以这样从所有起点开始吗？no，主要是之前起点都不明确