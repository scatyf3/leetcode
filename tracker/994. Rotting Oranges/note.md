# 994. Rotting Oranges


### pass2

1. 多源bfs，collect全部2，然后bfs
2. 但是我们要的距离和bfs的深度差1，bfs到的最后leaf还需要再扫一轮，确定全部没后续，所以res和外面的loop的counter差1
3. 何时mark，入队的时候mark腐烂，和之前collect的腐烂queue一样。否则会被重复入队

### pass1

1. 感觉更接近模拟+层序遍历，collect全部腐烂的橘子起点，然后per step模拟即可
2. 还是之前说的for _ in len(q) 省去俩队列


说起来我们前面做过的grid题可以这样从所有起点开始吗？no，主要是之前起点都不明确