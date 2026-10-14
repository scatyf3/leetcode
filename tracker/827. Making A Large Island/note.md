# 827. Making A Large Island

（2026-10-14 mock 抽到，只想了思路没写）

懒得做了，想下思路，最naive的解是

```
for each gird==0, set1
    dfs 算岛屿面积
```

这好像是O(n^4)，有什么优化方法吗，大部分都是浪费的，可以在不change 1的情况下算grid面积，
然后找能把俩岛屿连起来的变化点，如果找到的话就存变化点+变化后的面积，找最大

怎么定义变化点？每个岛屿周围的一圈，最少本岛+1

怎么判断周围的一圈0能否链接两个grid啊

---

### 思路：先把不变的部分算成表，再逐个 0 查表

naive 的浪费在于：每翻一个 0 都把**没变过的岛**重数一遍。岛的面积只算一次就够了。

| 遍 | 做什么 | 复杂度 |
|---|---|---|
| 第 1 遍 | 每个没编号的 1 出发 flood fill，整座岛写成同一个编号（从 **2** 开始），记 `area[编号] = 面积` | O(n²) |
| 第 2 遍 | 每个 0 看上下左右 4 个邻居属于哪些岛，`1 + sum(area[不同编号])` | O(n²) |

> 「每个候选位置都重算全局」太慢时，先把**不变的部分**预处理成表（编号 → 面积），候选位置只做查表 + 局部合并。

### 「变化点」从 0 出发，不从岛出发

「每座岛周围一圈」= 和这座岛相邻的 0。从 0 出发枚举，每个格子只看一次；从岛出发走一圈，
同一个 0 会被它周围几座岛各访问一遍，还得再去重。

### 能不能连两座岛：不用单独判断

邻居编号收进 set，看 set 大小就知道了，三种情况**同一个公式**：

```
2 2 0 3
2 0 0 3
0 0 4 0
```

| 位置 | 邻居编号 | set | 翻完面积 | 含义 |
|---|---|---|---|---|
| (0,2) | 左 2、右 3 | {2, 3} | area[2] + area[3] + 1 | 连起两座岛 |
| (1,1) | 上 2、左 2 | {2} | area[2] + 1 | 只是给岛 2 加一格 |
| (2,3) | 上 3、左 4 | {3, 4} | area[3] + area[4] + 1 | 连起两座岛 |
| (2,0) | 都是 0 | {} | 1 | 谁也没连上 |

编号从 2 开始：0 = 水、1 = 还没编号的陆地、≥ 2 = 已编号的岛，不用另开 visited。

### 解

```python
class Solution:
    def largestIsland(self, grid: list[list[int]]) -> int:
        n = len(grid)
        DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

        def fill(r, c, iid):                    # 迭代 flood fill, 返回面积
            grid[r][c] = iid
            stack, cnt = [(r, c)], 0
            while stack:
                r, c = stack.pop()
                cnt += 1
                for dr, dc in DIRS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 1:
                        grid[nr][nc] = iid      # 入栈时就标记, 防止重复入栈
                        stack.append((nr, nc))
            return cnt

        area, iid = {}, 2
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 1:
                    area[iid] = fill(r, c, iid)
                    iid += 1

        best = max(area.values(), default=0)    # 没有 0 可翻(全是 1)时答案就是最大的岛
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 0:
                    ids = {grid[r + dr][c + dc] for dr, dc in DIRS
                           if 0 <= r + dr < n and 0 <= c + dc < n and grid[r + dr][c + dc] > 1}
                    best = max(best, 1 + sum(area[i] for i in ids))
        return best
```

### 坑

- **邻居去重**：0 卡在 L 形岛的拐角，上和左是同一座岛，不用 set 会把面积加两次
- **全是 1**：没有 0 可翻，只在第 2 遍更新答案会返回 0 → `best` 先取最大岛面积（= n²）
- **全是 0**：`area` 为空，`default=0`；第 2 遍每个 0 给出 1 → 答案 1
- **递归 DFS 会爆栈**：n 最大 500，一座岛最多 25 万格，Python 默认递归深度 1000 → flood fill 用显式栈
- **入栈时标记**，不是出栈时：出栈才标记的话同一格会被几个邻居重复压栈，面积算多

自测：`[[1,0],[0,1]]` → 3，`[[1,1],[1,0]]` → 4，`[[1,1],[1,1]]` → 4，`[[0,0],[0,0]]` → 1。

相关：[structures/grid.md](../../blog/docs/structures/grid.md)；200 Number of Islands 是第 1 遍本身。
