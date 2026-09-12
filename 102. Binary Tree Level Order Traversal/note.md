# 102. Binary Tree Level Order Traversal


就是bfs，然后注意
1. deque的api，popleft是独有api
2. edge case，append下一层的时候要判断下是否为None, 否则silent error，当然也可以打印出deque看
3. 更好的写法，一个queue，每一层维护counter，省的维护cur和next俩队列