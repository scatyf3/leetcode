# 909. Snakes and Ladders


### pass2

1. indexing，用row index判断col index是否要reverse
2. snack and ladder，入队即判断jump，只判一次。如果出队再判断，则...，这也在其他case里出现过，如visited就是入队判断。

### pass1

1. indexing，这里的索引及其恶心，dim1是反的，dim0是蛇形的，你能否indexing对？
2. 算法，不能dp，这里有环形依赖，只能bfs。
3. 但bfs我的问题是，每个node都会fanout6个，这样的话是不是会bfs爆炸，如何减少复杂性？ => 用visited去重，实际的复杂度是 "有 visited → 每格只入队一次 → O(n²)
