---
title: 并查集（Union-Find）
status: draft
order: 22
alias: []
related: [/structures/graph, /paradigms/bfs, /paradigms/dfs]
---

# 并查集（Union-Find）

**每个点记一个上级，一路往上找到的那个点就是组长（根）。** 问 a、b 连没连通，就各自找到根比一比；
连一条边，就让一个根认另一个根当上级。不建邻接表，也不用 BFS，边来一条处理一条。

## SOP

步骤来自 [261](https://github.com/scatyf3/leetcode/blob/main/tracker/261.%20Graph%20Valid%20Tree/note.md) pass2
和 [684](https://github.com/scatyf3/leetcode/blob/main/tracker/684.%20Redundant%20Connection/note.md) 两遍的 note。

1. **先认信号：边一条一条给，问「连没连通」「加这条边会不会成环」。** 684 问的是「哪条边多余」，按输入顺序加边，第一条成环的边就是答案。
2. **`parent` 按点的下标存。** 261 pass2 的 note：存「点 → 组」的关系，不要按值去判断是不是一组，否则合并时要扫、要改的东西很多。684 的点是 1..n，`parent` 开 `n + 1`，下标 0 空着。
3. **加边前先 `find` 两端：同根 → 成环；不同根 → 一个根挂到另一个根下。** 合并只动根，见 §1。
4. **最后读答案。** 684 成环那一刻直接返回；261 还要查连通：边全加完，只剩一个组。
5. **要删边，就倒过来变成加边**（§3）。

第 3 步栽过的坑：

- **684**：合并写成改端点本体，`parent[b] = a`。684 pass2 的 note：「只操作 root，不能操作本体」，反例见 §1
- **261**：组号版合并前要先把 `to_replace` 存下来，否则它会在循环中途被改掉（sol2 的注释，§2）

## 1. 模板（684）

```python
def findRedundantConnection(edges):
    n = len(edges)                 # 树 + 1 条边 -> 点数 == 边数
    parent = list(range(n + 1))    # 点是 1..n, 下标 0 空着

    def find(idx):
        while idx != parent[idx]:  # 自己是自己的上级，就是根
            idx = parent[idx]
        return idx

    for edge in edges:             # 按输入顺序加边
        src, dst = edge
        root_src = find(src)
        root_dst = find(dst)
        if root_src == root_dst:   # 两端早就连通了，这条边多余
            return edge
        parent[root_dst] = root_src    # 只操作 root，不操作 src / dst 本体
```

**为什么只能动根。** `parent[dst] = src` 只把 dst 一个点搬走了，dst 原来那组里的其他点还挂在旧根下面，和 dst 断了联系。
`[[1,2],[3,2],[1,3]]`：第二条边把 2 从 1 底下摘走、挂到 3 下面，1 成了孤点；
第三条边 `find(1) = 1`、`find(3) = 3`，判成不同根，环漏掉了，返回 `[]`（应为 `[1,3]`）。
挂根就是整组一起搬，组里每个点往上找，找到的都是新根。

**为什么第一条成环的边就是答案。** 题目要「输入里最靠后的那条可删的边」。图里只有一个环，
按顺序加边，最后一条加进环的边，就是环上在输入里最靠后的那条。

**路径压缩**：684 的 `find` 没压缩，最坏一条链 O(n)，n ≤ 1000 照样过。
要压缩就在 `while` 里加一行 `parent[idx] = parent[parent[idx]]`：边往上走，边让自己直接挂到爷爷下面，树越走越扁。

## 2. 第一版：每个点直接存组号（261 sol2）

```python
union_find = [i for i in range(n)]        # union_find[i] = i 所在组的编号
for edge in edges:
    if union_find[edge[0]] == union_find[edge[1]]:
        return False                      # 已经一组，再连就成环
    to_replace = union_find[edge[1]]      # 先存下来，循环里它会被改掉
    to_merge = union_find[edge[0]]
    for idx, val in enumerate(union_find):
        if val == to_replace:
            union_find[idx] = to_merge
return len(set(union_find)) == 1          # 只剩一组 = 连通
```

查询 O(1)，合并要扫整个数组 O(n)。684 那版正好反过来：合并只改一个根，代价挪到 `find` 往上走的那几步。

不存 `to_replace`、循环里直接比 `union_find[edge[1]]`：`n = 3, [[0,1],[2,0]]` 这棵树，
第二条边扫到下标 0 时就把 `union_find[0]` 改成了 2，下标 1 再比就对不上，最后是 `[2,0,2]`，返回 False。

## 3. 和 BFS 比（261）

| | BFS（261 sol） | 并查集（261 sol2、684） |
|---|---|---|
| 建图 | 邻接表，无向边两头都加 | 不建 |
| 判环 | 先判 `len(edges) == n - 1`，之后不用查环 | 加边时两端同根 → 成环 |
| 判连通 | 从 0 走，`len(visited) == n` | 最后只剩一组 |

261 两种都行，BFS 的思路见 [bfs.md](bfs.md) §6。684 就不适合 BFS：
每加一条边都得重新搜一遍「两端是不是已经连通」；并查集每条边只做两次 `find`。

## 4. 删除难做，倒过来变成添加（684）

684 pass1 问过：为什么是从空图往上加，而不是从完整的图开始检测、删除？因为并查集只会合并，不会拆开。可以记成一个套路：

- 「第一次出现某个情况是什么时候」→ 按顺序加，加到它出现为止（684）
- 「一个个删，问每次删完的状态」→ 把时间倒过来：从全删完的状态开始，往回一个个加。
  803 Bricks Falling When Hit 就是这个形状：先把要打的砖全打掉，再倒着一块块补回去（还没做）
