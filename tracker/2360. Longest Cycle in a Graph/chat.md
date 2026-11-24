<!-- chat df5f19da/85d0a7c8 2026-11-22 -->

#### 🧑 我

2360. Longest Cycle in a Graph


```python
class Solution:
    def longestCycle(self, edges: list[int]) -> int:
        # bfs with kahn to remove non-loop

        # compare loopsize for each loop?
```


是这样的吗

#### 🤖 Claude

对，这思路是成立的，而且两步都不复杂：Kahn 删完之后，剩下的**全是互不相交的简单环**，逐个数长度取最大就行。

原因是每个点最多一条出边，所以环上的点唯一的出边已经用在环里了，不会再伸出别的边。剩下的点入度和出度都恰好是 1，从任意一点沿着 `edges` 走，一定会回到自己。这和你最近做的 2127 找环那部分一样。

写的时候注意三点：

1. **`edges[i] == -1` 要判断。** Python 里 `indeg[-1] += 1` 不报错，会悄悄加到最后一个点上。算入度和 Kahn 出队时都要判。
2. **没有环返回 -1**，所以 `res` 的初值想一下。
3. **数环时每个环只走一遍。** 走过的点要标记，不然每个点都绕一圈，单个大环会退化成 O(n²)。

先把骨架补成这样，再往里填：

```python
# 1. 算入度（跳过 -1）
# 2. Kahn：入度 0 的入队，删点，后继入度 -1，变 0 就入队
# 3. 剩下没删的点：沿 edges 走一圈，边走边标记，数长度
# 4. 返回最大值，没有环返回 -1
```

第 3 步有个问题可以先想想：Kahn 已经有一个「删没删」的标记了，数环时要不要另开一个 `visited`？

#### 🧑 我

```python
class Solution:
    def longestCycle(self, edges: list[int]) -> int:
        # bfs with kahn to remove non-loop
        g = {}
        n = len(edges)
        indeg = [0 for i in range(n)]
        for src,dst in enumerate(edges):
            if src in g:
                g[src].append(dst)
            else:
                g[src]=[dst]
            indeg[dst]+=1
        start=[]
        for dst in range(n):
            if indeg[dst]==0:
                start.append(dst)
        q = deque(start)
        while q:
            q_len=len(q)
            for _ in range(q_len):
                cur_node = q.popleft()
                for next_node in g[cur_node]:
                    indeg[next_node]-=1
                    if indeg[next_node]==0:
                        q.append(next_node)
        all_zeros=True
        cand_st=set()
        cand = []
        for dst in range(n):
            if indeg[dst]!=0:
                all_zeros=False
                cand.append(dst)
                cand_st.add(dst)
        if all_zeros:
            return -1
        visited = set()
        res=0
        for node in cand:
            if node in cand_st:
                cur=0
                q = deque([node])
                while q:
                    q_len=len(q)
                    for _ in range(q_len):
                        cur_node = q.popleft()
                        for next_node in g[cur_node]:
                            if next_node in cand_st:
                                cur+=1
                                q.append(next_node)
                                cand_st.remove(next_node)
            res=max(cur,res)
        return res
```


这玩意怎么处理-1

#### 🤖 Claude

**建图时跳过，同时给每个点预留空列表**：

```python
g = [[] for _ in range(n)]
indeg = [0] * n
for src, dst in enumerate(edges):
    if dst != -1:
        g[src].append(dst)
        indeg[dst] += 1
```

后面都不用改。`-1` 的点对应 `g[src] == []`，`for` 循环自然什么都不做。如果留着 dict 只加 `continue`，没有出边的点就不在 `g` 里，后面 `g[cur_node]` 会 KeyError。

现在的写法会把 `-1` 当成最后一个点。比如 Example 2 `[2,-1,3,1]`，`indeg[-1]` 加到了点 3 上，凭空多了一条 1→3，点 1 和 3 就删不掉了，返回 1，正确答案是 -1。

其余逻辑是对的：起点一开始没从 `cand_st` 移除，绕回来时才移除并计数，所以 `cur` 正好是环长。

能过之后可以再精简：

- **不用 `g`**：每个点最多一条出边，`edges` 本身就是图，用 `edges[cur_node]` 就行，只是每次要判断 `-1`。
- **不用 `q_len` 分层**：你没有用到层数，`while q: popleft()` 就够了。
- **数环不用 BFS**：环上只有一条路，一个指针往前走即可。
- **删掉 `visited`、`all_zeros`**：前者没用到；后者可以让 `res` 初值为 -1。

#### 🧑 我

```python
class Solution:
    def longestCycle(self, edges: list[int]) -> int:
        # bfs with kahn to remove non-loop
        g = {}
        n = len(edges)
        indeg = [0 for i in range(n)]
        for src,dst in enumerate(edges):
            if dst!=-1: #skip -1
                if src in g:
                    g[src].append(dst)
                else:
                    g[src]=[dst]
                indeg[dst]+=1
            else:
                g[src]=[]
        start=[]
        for dst in range(n):
            if indeg[dst]==0:
                start.append(dst)
        q = deque(start)
        while q:
            q_len=len(q)
            for _ in range(q_len):
                cur_node = q.popleft()
                if cur_node not in g:
                    return -1
                for next_node in g[cur_node]:
                    indeg[next_node]-=1
                    if indeg[next_node]==0:
                        q.append(next_node)
        all_zeros=True
        cand_st=set()
        cand = []
        for dst in range(n):
            if indeg[dst]!=0:
                all_zeros=False
                cand.append(dst)
                cand_st.add(dst)
        if all_zeros:
            return -1
        visited = set()
        res=0
        for node in cand:
            if node in cand_st:
                cur=0
                q = deque([node])
                while q:
                    q_len=len(q)
                    for _ in range(q_len):
                        cur_node = q.popleft()
                        for next_node in g[cur_node]:
                            if next_node in cand_st:
                                cur+=1
                                q.append(next_node)
                                cand_st.remove(next_node)
            res=max(cur,res)
        return res
```


            
            


这个complexity对吗

#### 🤖 Claude

对，时间 O(n)，空间 O(n)，已经最优。看着有三层循环，但要按**总共处理多少次**来算：

| 部分 | 为什么是 O(n) |
|---|---|
| 建图 | 每个点看一次 |
| Kahn | 每个点最多入队一次，每个点最多一条出边，总共最多 n 条边 |
| 数环 | 每走一步就从 `cand_st` 删一个点，总共最多删 n 次；每个环只多入队一次起点 |

`while` 加 `for _ in range(q_len)` 只是把同一个队列分批弹出，不会让总次数变多。

逻辑也对，只有一处要删：

```python
if cur_node not in g:
    return -1
```

现在每个点都在 `g` 里，这段永远不会执行。而且它的含义是错的：某个点没有出边，不代表整张图没有环。比如 `[1,0,-1]`，点 2 没有出边，但 0 和 1 成环，答案是 2。

剩下的 `visited`、`all_zeros`、`q_len` 可以顺手清掉，不影响复杂度。

#### 🧑 我

还有哪里可以删

#### 🤖 Claude

能删的还不少，核心是 `g`、`cand`、`cand_st` 都可以用现成的数组代替：

| 删掉 | 用什么代替 |
|---|---|
| `g` | `edges`，每点最多一条出边，它就是图 |
| `cand`、`cand_st` | `indeg`，`> 0` 就是还在环上；走过设成 0 |
| 数环的 `q` | 一个指针往前走 |
| `all_zeros` | `res` 初值 -1 |
| `visited`、`q_len`、`if cur_node not in g` | 直接删 |

删完是这样：

```python
class Solution:
    def longestCycle(self, edges: list[int]) -> int:
        n = len(edges)
        indeg = [0] * n
        for dst in edges:
            if dst != -1:
                indeg[dst] += 1

        # Kahn：删掉不在环上的点
        q = deque(i for i in range(n) if indeg[i] == 0)
        while q:
            nxt = edges[q.popleft()]
            if nxt != -1:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    q.append(nxt)

        # 剩下 indeg > 0 的都在环上，逐个环数长度
        res = -1
        for start in range(n):
            node, cur = start, 0
            while indeg[node] > 0:
                indeg[node] = 0      # 标记走过
                node = edges[node]
                cur += 1
            if cur > 0:
                res = max(res, cur)
        return res
```

两个细节：

- **数环时不用判 `-1`**：环上的点一定有出边。
- **`if cur > 0` 不能删**：否则不在环上的点会用 0 盖掉 -1，没有环时就返回 0 了。

复杂度还是 O(n)，只是空间常数小了。
