
### concept

1. 入队时修改，否则会重复入一些队，导致overhead
2. 可以多源，很多个source一起
3. 分层 BFS 与步数差一：用 for _ in range(len(q)) 分层；分清你数的是层数还是步数（或分钟数），最后一层是白跑的。用 while q and 还有目标 可以避开差一，这是今天的错 2
4. 可能要统计另外一类格子的数量
5. 可能要反着搜，减少搜索计算量


### implementation

这里都是2d grid，有很多小细节
1. check是否越界 两个` 0<=idx<len`
2. 怎么在2d grid上找next，设置个next offset小数组，然后for，然后直接add到我们的坐标上
3. 不用搞visit set，inplace改grid的内容；如果不能inplace，只存visited和seen就set，如果再复杂就grid
4. grid里有可能是char有可能是int