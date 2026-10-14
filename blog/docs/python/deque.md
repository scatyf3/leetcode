---
title: deque
status: draft
order: 3
related: [/structures/stack-queue, /structures/linked-list, /paradigms/bfs, /paradigms/sliding-window]
---

# deque

## 一句话

**定长块串成的双向链表**。两端进出都是 O(1)；按下标访问中间是 O(n)。

## 底层长什么样

不是一个节点一个元素的链表，而是每块 64 格的数组，块之间双向链接。两端各有一个指针指着用到哪格：

```
     left                                   right
      ↓                                       ↓
[ _ _ _ a b c ] ⇄ [ d e f g h i ] ⇄ [ j k l _ _ _ ]
```

头部满了就往前挂一块新的，尾部满了往后挂一块，**从不整体挪元素** —— 这就是两端 O(1) 的来历。
代价是没法直接算出第 i 个在哪，只能从近的那端一块块数过去。

## 复杂度

| 操作 | 复杂度 |
|---|---|
| `append` / `appendleft` / `pop` / `popleft` | O(1) |
| `q[0]` / `q[-1]` | O(1) |
| `q[i]`（中间） | O(n) |
| `x in q` / `remove(x)` | O(n) |
| `rotate(k)` | O(k) |
| `len(q)` | O(1) |

## 由此而来的坑

- **在 `collections` 里**：`from collections import deque`，不是内置。
- **不能切片**：`q[1:3]` 直接 `TypeError`。要切先 `list(q)`，或者用 `itertools.islice`。
- **把 deque 当数组随机访问**：单调队列里只看两端没问题，中间按下标读就退化了。
- **BFS 分层**：先 `for _ in range(len(q))` 再出队，`len` 要在循环开始前取定。
- **`deque(maxlen=k)`** 满了会从另一端**静默**挤掉元素，不报错。

## 当队列 / 单调队列用

BFS：`append` 进，`popleft` 出。滑动窗口最大值（LC 239）：队里存下标、保持对应值单调递减，
队头过期就 `popleft`，新元素比队尾大就 `pop` —— 两端都要 O(1)，所以只能是 deque。

语法卡：[tracker/syntax/deque.md](https://github.com/scatyf3/leetcode/blob/main/tracker/syntax/deque.md)
