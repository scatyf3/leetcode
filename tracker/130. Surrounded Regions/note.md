# 130. Surrounded Regions

### pass2
1. 开动脑筋，反向思考
2. 怎么遍历2d grid的边，`if (i==0 or i==m-1 or j==0 or j==n-1) and board[i][j]=="O"`，注意条件之间的括号
3. 维护一个mask，入队的时候加mask，记得第一轮也一样。之前的橘子是把mask送给你了（

### pass1
1. 和上一道题一样，保留全部start，然后从多个start bfs写起来省事
2. 反向思考，从边搜索保留的，而不是搜可以被replace