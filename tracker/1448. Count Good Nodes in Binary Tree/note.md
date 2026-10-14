# 1448. Count Good Nodes in Binary Tree
1. 一个node是不是good，只有递归到最底下知道，需要的信息是逐步传下去的prefix max
2. 然后这里修改global max比较好，若答案写到返回值里，shared prefix上的good node会重复统计