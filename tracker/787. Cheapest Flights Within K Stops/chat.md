<!-- chat a6adab16/1078384b 2026-11-10 -->

#### 🧑 我

787 Cheapest Flights Within K Stops

这部分是没算法是吗

#### 🤖 Claude

对，你的笔记里还没有这一类。我搜了 blog 和 tracker：

- [bfs.md:12](blog/docs/paradigms/bfs.md#L12) 只讲到**无权图**的最短路，就是一个点第一次被碰到时走的路最短。
- 整个仓库里没有出现过 Dijkstra 或 Bellman-Ford，也没有哪道题处理过**带权**的边。
- [graph.md](blog/docs/structures/graph.md) 讲的是建图、visited、判环、拓扑排序，同样不涉及边权。

不过 787 本身是有标准算法的。它是**带权最短路，再加一个"最多经过 k 站"的限制**，这正好是你笔记里还没覆盖的部分。

先给一级提示，答案不展开：

> 拿你已经会的 BFS 想一下：一个城市**第一次**被碰到时，用的边数最少，但花的钱不一定最少。反过来，最便宜的那条路可能要经过很多站，超过 k 的限制。所以这题有两个量要同时管：**花了多少钱**、**走了几条边**，只盯其中一个都不行。

想好以后可以接着往下问，我再给第二级提示：在这两个量之间怎么取舍。做完这题，可以在 bfs.md 里加一节"带权的时候 BFS 为什么不够用"，或者单独新开一篇讲最短路。

#### 🧑 我

```python
class Solution:
    def findCheapestPrice(self, n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
        # bfs 探测从src走k步reachable，path及其cost，然后检查dst是否在其中，
        # 如果在的话，最小的是什么（直接bfs的时候动态update最小，以防explicit存多个路径）
```


这个思路对吗

#### 🤖 Claude

大方向是对的：按层 BFS，最多走固定的层数，层数用来管边数，过程中顺手更新到达 dst 的最小花费。下面三点要再想清楚。

### 1. 层数差一

题目限制的是"最多中转 k 站"，k 站中转对应 **k+1 条边**。所以 BFS 要扩展 k+1 层，不是 k 层。这题最常见的 WA 就是这里少算一层。

### 2. 不要存路径

队列里放 `(城市, 到这里花的钱)` 就够了。你注释里写的"动态 update 最小"是对的方向，再往前推一步：只要知道一个城市当前的花费，后面怎么走都和之前经过了哪些城市无关。

### 3. 这一点最关键：用什么去重？

不去重的话，同一个城市每一层都可能被很多条路径反复塞进队列，状态数会按层指数增长。上一轮说过，普通 BFS 的 visited（第一次碰到就标记、以后不再进）在这题不能用，因为第一次到达的那条路不一定最便宜。

问你一个问题：

> 第 i 层到达城市 v，花费是 c。之后在第 j 层（j > i）**又**到达 v，花费是 c' ≥ c。后面这次还有必要继续往下扩展吗？

想清楚这个问题，就知道该用什么数组、在入队前怎么剪枝了。还可以顺带想一下：**为什么这个判断只在按层推进的 BFS 里成立？** 想到这一层，你会发现自己写出来的东西其实就是 Bellman-Ford，只是限制了轮数。

写完代码贴过来，我帮你看边界。

#### 🧑 我

visited直接用最小cost呗，然后一个path update下cost即可

#### 🤖 Claude

对，这个思路是对的。visited 只回答"去没去过"，改成记录"到这个城市的最低花费"：新的路径更便宜才更新并入队，否则丢掉。

它成立的原因是 BFS 一层一层往外走，层数越往后，用的边数越多。所以后来到达同一个城市的路径，边数一定不比之前少；如果钱也不比之前少，这条路在两个维度上都不占优，以后怎么走都不会比之前那条好。这正好回答了上一轮的问题。

写代码时有两个地方容易写错：

1. **扩展邻居时，用队列里存的那个 cost，不要用 `best[u]`。** 同一层处理的过程中，`best[u]` 可能已经被这一层的另一个节点改成更小的值了，而那个值对应的路径多走了一条边。拿它去扩展，等于一层里连走了两条边，k 的限制就失效了。这也是 Bellman-Ford 每轮要先复制一份 dist 的原因，是同一个坑。
2. **不要加"出队时 `c > best[u]` 就跳过"这种剪枝。** 写 Dijkstra 的习惯会让人想加这一句，但在这题里，`best[u]` 可能是下一层的某条路径刚刚更新的：钱更少，可边更多。按它跳过，就会扔掉一条边数更少、本来还能继续扩展的路径。

剩下的就是层数取 **k+1**，最后 `best[dst]` 如果还是 inf，就返回 -1。复杂度是 O((k+1)·E)。

可以开始写了，写完贴过来。

#### 🧑 我

```python
class Solution:
    def findCheapestPrice(self, n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
        # bfs 探测从src走k步reachable，path及其cost，然后检查dst是否在其中，
        # 如果在的话，最小的是什么（直接bfs的时候动态update最小，以防explicit存多个路径）
        # talk with agent: visited直接用最小cost呗，然后一个path update下cost即可

        cost_table = {}
        flight_table = {} # src => [(dst,cost)]
        for src,dst,cost in flights:
            if src in flight_table:
                flight_table[src].append((dst,cost))
            else:
                flight_table[src]=[(dst,cost)]
        # print(flight_table)
        # {0: [(1, 100)], 1: [(2, 100), (3, 600)], 2: [(0, 100), (3, 200)]}
        q = deque([(src,0)])
        cost_table[src]=0
        cnt = k+1
        while cnt>0 and q:
            q_len = len(q)
            for _ in range(q_len):
                cur_node,cur_cost = q.pop()
                # accumulate cost
                for cur_dst,cost in flight_table[cur_node]:
                    if cur_dst in cost_table and cur_cost+cost<cost_table[cur_dst]:  
                        # should the cost less than current to be inqueue?
                        cost_table[cur_dst]=min(cost_table[cur_dst],cur_cost+cost)
                        q.append(cur_dst)
                    if cur_dst not in cost_table:
                        cost_table[cur_dst]=cur_cost+cost
                print(cost_table)
                cnt-=1
            
        if dst in cost_table:
            return cost_table[dst]
        else:
            return -1
```


这哪里不对了，为啥我们的cost table只print一次

#### 🤖 Claude

只打印一次，是因为第一个节点出队以后，队列就空了：**第一次到达的城市只写进了 `cost_table`，没有入队**。

```python
if cur_dst not in cost_table:
    cost_table[cur_dst] = cur_cost + cost   # ← 没有 append
```

只有"已经到过、而且这次更便宜"的城市才会入队。第一层碰到的城市全是第一次到达，所以没有一个进队列。外层 `while` 再检查时 `q` 已经空了，循环直接结束，`print` 只执行了一次。

除了这个，还有五个 bug：

1. **`src` 和 `dst` 被覆盖了。** 建表时写的是 `for src, dst, cost in flights`，循环结束后，函数参数 `src`、`dst` 变成了最后一条航班的起点和终点。用题目的样例跑，BFS 是从 2 出发的，不是从 0。循环变量换个名字，比如 `u, v, w`，就好了。
2. **`q.pop()` 从右边弹出，新节点又 `append` 在右边**，这样队列其实是个栈：这一层刚加进去的节点，会在同一层的 `for` 循环里被弹出来，层就混在一起了，k+1 的限制也就失效了。要改成 `popleft()`。
3. **`q.append(cur_dst)` 只放了城市，没放花费。** 下一层执行 `cur_node, cur_cost = q.pop()` 时，拆包会报错。要放 `(cur_dst, 新花费)`。这也是上一轮说的第一个坑：扩展邻居要用队列里带的 cost，所以入队时必须把 cost 一起带上。
4. **`cnt -= 1` 和 `print` 缩进进了 `for` 循环。** 现在每弹出一个节点就减一次，应该是每处理完一层才减一次。
5. **`flight_table[cur_node]` 会 KeyError。** 没有出边的城市，比如样例里的 3，不在这个表里。用 `defaultdict(list)` 或者 `.get(cur_node, [])` 都可以。

你注释里问"应该比当前更小才入队吗"：**是的，严格小于才入队。** 第一次到达也可以算作"比 inf 小"。这样两个分支就能合成一个：

```python
new_cost = cur_cost + cost
if new_cost < cost_table.get(cur_dst, float('inf')):
    cost_table[cur_dst] = new_cost
    q.append((cur_dst, new_cost))
```

这样写不用单独处理"第一次到达"，今天这个漏入队的 bug 就不会出现。

改完以后用这组样例自测：`n=4, flights=[[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]], src=0, dst=3, k=1`，应该返回 **700**。k=1 时只能走 0→1→3，0→1→2→3 虽然只要 400，但中转了两站，超过了限制。

#### 🧑 我

```python
class Solution:
    def findCheapestPrice(self, n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
        # bfs 探测从src走k步reachable，path及其cost，然后检查dst是否在其中，
        # 如果在的话，最小的是什么（直接bfs的时候动态update最小，以防explicit存多个路径）
        # talk with agent: visited直接用最小cost呗，然后一个path update下cost即可

        cost_table = {}
        flight_table = {} # src => [(dst,cost)]
        for isrc,idst,cost in flights: # do not use src and dst, it will override input
            if isrc in flight_table:
                flight_table[isrc].append((idst,cost))
            else:
                flight_table[isrc]=[(idst,cost)]
        # print(flight_table)
        # {0: [(1, 100)], 1: [(2, 100), (3, 600)], 2: [(0, 100), (3, 200)]}
        q = deque([(src,0)])
        cost_table[src]=0
        cnt = k+1
        while cnt>0 and q:
            q_len = len(q)
            for _ in range(q_len):
                cur_node,cur_cost = q.popleft()
                # accumulate cost
                if cur_node in flight_table:
                    for cur_dst,cost in flight_table[cur_node]:
                        if cur_dst in cost_table and cur_cost+cost<cost_table[cur_dst]:  
                            # should the cost less than current to be inqueue?
                            cost_table[cur_dst]=min(cost_table[cur_dst],cur_cost+cost)
                            q.append((cur_dst, cur_cost+cost))
                        if cur_dst not in cost_table:
                            cost_table[cur_dst]=cur_cost+cost
                            q.append((cur_dst, cur_cost+cost))
                    # print(cost_table)
                cnt-=1
            
        if dst in cost_table:
            return cost_table[dst]
        else:
            return -1
```



```
Input
n =
5
flights =
[[1,0,5],[2,1,5],[3,0,2],[1,3,2],[4,1,1],[2,4,1]]
src =
2
dst =
0
k =
2
Output
10
Expected
```


好像还不对

#### 🤖 Claude

只剩一个 bug：**`cnt -= 1` 还在 `for` 循环里面**。它的缩进和 `if cur_node in flight_table` 一样，所以每弹出一个节点就减一次，而不是每处理完一层减一次。要往左退一级，和 `for _ in range(q_len):` 对齐。

用你这组输入走一遍。src=2，k=2，cnt 初始是 3：

| 弹出 | 做了什么 | cnt |
|---|---|---|
| 第 1 层：(2, 0) | 1 = 5，4 = 1 | 3 → 2 |
| 第 2 层：(1, 5) | **0 = 10**，3 = 7 | 2 → 1 |
| 第 2 层：(4, 1) | 1 更新为 2，入队 | 1 → **0** |

第 2 层刚处理完，cnt 就已经减到 0，循环结束。第 3 层根本没跑，所以返回了 10。

把缩进改对以后，第 3 层会处理 `(0,10)`、`(3,7)`、`(1,2)` 这三个节点：

- 处理 (3, 7) 时，经过 3→0 把 0 更新成 9；
- 处理 (1, 2) 时，经过 1→0 把 0 更新成 **7**。

7 就是正确答案，对应的路径是 2→4→1→0，3 条边，中转 2 站。还有一条 2→4→1→3→0 只要 6，但它有 4 条边、中转 3 站，超过了 k=2，所以不能算。这组样例正好卡在"更便宜但边更多"上，可以留着当自测用例。

另外还有两处可以顺手简化，不影响对错：
- `min(cost_table[cur_dst], cur_cost + cost)` 里的 `min` 是多余的，进到这个分支时已经确定新值更小了；
- 两个 `if` 分支可以合成一个，用上一轮那个 `.get(cur_dst, inf)` 的写法就行。
