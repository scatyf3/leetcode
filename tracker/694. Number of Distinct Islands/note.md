# 694. Number of Distinct Islands

0. dfs不太标准
1. 怎么返回cur_island不熟练
2. 怎么给offset不熟练
3. 最后怎么去重不会，直接每个list转换为hashable，这里用string


标准的dfs？
1. 无脑调用
2. 在每个开始判断是否valid

```python
def dfs(x, y):
    if not (0 <= x < len(grid) and 0 <= y < len(grid[0])) or grid[x][y] != 1:
        return
    grid[x][y] = 0                 # 处理自己：标记
    cur_island.append((x, y))      #           记录
    for dx, dy in nxt:
        dfs(x + dx, y + dy)        # 邻居不用检查，交给下一层
```

但是相反，用队列的bfs不能这么写，主要是没有这个检查，最好是入队的时候标一下。或者至少出队检查

```python
grid[sr][sc] = 0
q = deque([(sr, sc)])
while q:
    x, y = q.popleft()
    for dx, dy in DIRS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
            grid[nx][ny] = 0             # 入队就标
            q.append((nx, ny))
```