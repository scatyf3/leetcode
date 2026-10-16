---
title: BFS
status: draft
order: 8
alias: []
related: [/python/deque, /structures/graph, /structures/grid, /structures/tree, /paradigms/dfs]
---

# BFS

**往水里扔一块石头，波纹一圈一圈往外扩。** 先处理离起点 1 步的所有点，再处理 2 步的，再处理 3 步的……
所以一个点**第一次**被碰到时，走的就是最短的那条路 —— 无权图的最短路就是 BFS。

```
      2
    2 1 2          S 是起点
  2 1 S 1 2        数字 = 第几圈被碰到 = 离 S 几步
    2 1 2
      2
```

实现上就是一个**先进先出**的队列：先进来的（近的）先出去处理，它的邻居排到队尾（远一圈）。
把队列换成栈，同一份代码就成了 DFS（[stack-queue.md](../structures/stack-queue.md)）。

## 1. 骨架

417 sol2 里的 `bfs`，后面的题几乎都是它的变形：

```python
def bfs(starts):
    seen = set(starts)              # 起点也要先放进 seen
    q = deque(starts)
    while q:
        r, c = q.popleft()
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if (0 <= nr < m and 0 <= nc < n
                    and (nr, nc) not in seen
                    and heights[nr][nc] >= heights[r][c]):   # 这题自己的「能不能走」
                seen.add((nr, nc))  # 入队即标
                q.append((nr, nc))
    return seen
```

两条规矩：

- **队列用 `deque`，出队用 `popleft()`**。`popleft` 是 deque 独有的 API（102 的 note）；拿 list 的 `pop(0)` 是 O(n)，见 [list.md](../python/list.md)。
- **入队时就标记，不要等出队**。出队才标的话，同一格在出队前会被好几个邻居各推一次，重复的格子又各自去扩展邻居 ——
  200 的第一版就这样 TLE 了。**起点也一样**，入队前就标（130：「记得第一轮也一样」）。
  标在哪（原地改 grid / `set` / 映射表）和 DFS 一样，见 [dfs.md](dfs.md) §5。

## 2. 分层：每层开头先记下 `len(q)`

要「按层」输出、或者要数走了几步时，在每一层开头先记下这一层有几个，只弹这么多（102 sol2）：

```python
def levelOrder(root):
    if not root:
        return []
    res = []
    q = deque([root])
    while q:
        level = []
        for _ in range(len(q)):        # len 在进 for 之前算好，锁住当前层
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        res.append(level)
    return res
```

`range(len(q))` 只在循环开始时求值一次，这一层新 append 进来的孩子不会被这一层弹掉。
102 的第一版用 `cur` / `next` 两个队列来回换，要多管一次「换层」，这个写法把它省掉了。

- **孩子先判 `None` 再入队**。`None` 进了队不会马上报错，要到下一轮取 `.val` 才炸（102）。
- **199 右视图**：同一个骨架，每层**最后一个**出队的就是从右边看到的。这依赖层内顺序是左 → 右，
  所以 frontier 必须是队列；换成栈，层内顺序会被打乱（199 的 note，对比表见 [stack-queue.md](../structures/stack-queue.md)）。

## 3. 层数 ≠ 步数：最后一层是白跑的（994）

994 烂橘子：每过一分钟，烂橘子把上下左右的新鲜橘子传染。分钟数就是 BFS 的层数 —— 但**差一**：
最后一层橘子出队后已经没有能传染的了，那一轮不该算一分钟。sol.py：

```python
def orangesRotting(grid):
    q = deque()
    m = len(grid)
    n = len(grid[0])
    fresh_counter = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j))               # 所有烂橘子一起当起点（§4）
            if grid[i][j] == 1:
                fresh_counter += 1

    nxt = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    max_len = 0
    while len(q) != 0 and fresh_counter > 0:   # 还有新鲜的才继续
        cur_layer_len = len(q)
        while cur_layer_len > 0:
            cur = q.popleft()
            for offset in nxt:
                next_pos = (cur[0] + offset[0], cur[1] + offset[1])
                if 0 <= next_pos[0] < m and 0 <= next_pos[1] < n and grid[next_pos[0]][next_pos[1]] == 1:
                    q.append(next_pos)
                    grid[next_pos[0]][next_pos[1]] = 2   # 入队就标
                    fresh_counter -= 1
            cur_layer_len -= 1
        max_len += 1
    if fresh_counter != 0:
        return -1
    else:
        return max_len
```

sol.py 注释里记着的三个错：

| 写法 | 后果 |
|---|---|
| 只写 `while q`，层数当分钟 | 多算最后那层，`[[2]]` 返回 1；改成从 -1 开始数，又在 `[[0]]` 上返回 -1 |
| 没数新鲜橘子 | BFS 走不到的孤立新鲜橘子，没法判 -1 |
| 出队才标 2 | 同一格跨层重复入队，多算一层：`[[2,1,1,2]]` 返回 2 |

> 把「还有目标」写进 `while` 条件，比事后再减一更不容易错。BFS 不知道你在数层还是数步，什么时候停得你自己定。

## 4. 多源：一群起点一起入队

994 里所有烂橘子同时开始传染，就把它们一起入队当第 0 层。这不是特殊技巧。心智模型（417 的 note）：
**虚构一个超级起点，连向所有真起点，从它做普通的单源 BFS**。把真起点一起入队，正好是替超级起点走完了第一步。

```
       (超级起点)
       /   |   \
     s1   s2   s3        ← 一起入队 = 第 0 层
```

| 题 | 起点 |
|---|---|
| 994 | 所有烂橘子 |
| 130 | 边界上所有的 `O` |
| 417 | 太平洋 = 上边 + 左边，大西洋 = 下边 + 右边，各搜一遍 |
| 207 | 所有入度为 0 的课（§6） |

200 数岛屿不是多源：每座岛要分开数，所以是外层循环扫格子，碰到没沉的陆地就从它搜一次，搜了几次就是几座岛。

## 5. 反着搜：从共享的那一端出发（417、130）

417 正着问：每个格子「我能流到海吗」。这是 m·n 个互不相干的问题，从 (1,1) 搜完的 `seen` 对 (2,3) 没用，
只能清空重来，O((mn)²)。反着问：「从海边逆流往上爬，能爬到谁」。所有格子共享同一个目标（海），
一次多源搜索就把答案全标出来，O(mn)。

> **目标端共享、起点端独立 → 从共享的那端出发。**

反着走，边的方向也要反：水往低处流（邻居 `<=` 自己），逆流就只走 `heights[邻居] >= heights[当前]` 的格子。
§1 的骨架就是 417 的 `bfs`，最后 `bfs(pac_starts) & bfs(atl_starts)` 两个可达集合取交集。

130 同理：不找「会被包围的 `O`」，找「和边界连通的 `O`」。边界上的 `O` 入队并标 `#`，BFS 完以后 `#` 还原成 `O`，其余全改 `X`。
判边界写 `(i in (0, m-1) or j in (0, n-1)) and board[i][j] == 'O'`，前半要加括号（130 的 note）。

## 6. 拓扑排序（Kahn）：所有前置都完成才入队（207）

207 的 BFS 和前面的不一样：一个点**不是**「有一个邻居到了就能入队」，而是「**所有**前置都完成了才能入队」。

| | 普通 BFS（417） | Kahn（207） |
|---|---|---|
| 什么时候入队 | 任意一个邻居走到了它（OR） | 所有前置都处理完（AND） |
| 靠什么判断 | `seen`：来过没有 | `indeg[v]`：还差几个前置没修完 |

```python
def canFinish(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]   # graph[u] = 修完 u 以后会解锁哪些课
    indeg = [0] * numCourses

    for a, b in prerequisites:                # [a, b] = 先修 b 才能修 a
        graph[b].append(a)
        indeg[a] += 1

    q = deque([i for i in range(len(indeg)) if indeg[i] == 0])
    taken = 0

    while q:
        u = q.popleft()
        taken += 1
        for v in graph[u]:
            indeg[v] -= 1                     # 修完 u，v 少一个前置
            if indeg[v] == 0:                 # 前置全修完才入队
                q.append(v)

    return taken == numCourses
```

有环时，环上的课入度永远减不到 0，永远进不了队，所以 `taken < n` ⇔ 有环。
只靠 visited 判环是错的：`0→1→2、0→2` 里 2 会被碰到两次，但没有环。DFS 写法要三种状态，见 [graph.md](../structures/graph.md)。
入度数组也不是用来「找起点」的，是给每个点计数「还差几个前置」；从入度 0 出发只是 AND 规则的自然结果（207 的 note）。

## 7. BFS 还是 DFS

- 问**最少几步 / 按层** → 只能 BFS（102、199、994）。
- 只问**能不能到** → 两个都对，遍历顺序无所谓（200、130、417）。这时选 BFS 往往是工程理由：
  417 在 200×200 全同高度时，递归 DFS 深度能到 4 万层，远超 Python 默认的 1000（[dfs.md](dfs.md) §6）；
  而且多源时整圈边界一次入队，写法和超级起点的模型一一对应。
- **走遍就行**的也都可以：133 用 BFS 走一遍建 `原 → 克隆` 表，再照原图的边给克隆连线；
  297 也能层序 —— 空节点写 `#` 照样占位，反序列化时每出队一个非空节点，就按顺序读两格当它的左右孩子。主线写法（前序）见 [dfs.md](dfs.md) §4。

## 8. 坑

- 133：给克隆连边时放进 `neighbors` 的是 `mp[neigh]`（克隆），不是原节点 `neigh`。
- 207：`[a, b]` 是「先修 b」，边是 `b → a`、`indeg[a] += 1`，sol.py 前两个坑就是这两处。
- 网格上的越界判断、方向数组见 [grid.md](../structures/grid.md)。
