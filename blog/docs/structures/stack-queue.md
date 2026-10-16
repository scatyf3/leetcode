---
title: 栈 / 队列
status: draft
order: 3
alias: [stack]
related: [/python/list, /python/deque, /paradigms/stack, /paradigms/bfs, /paradigms/sliding-window]
---

# 栈 / 队列

**在数组 / 链表上多维护一样东西：插入时间。** 栈只碰最晚进来的，队列只碰最早进来的。
放弃了「按下标随便拿」，换来的是「下一个该处理谁」不用想。

```
栈（LIFO）    append →  [ a  b  c  d ]  → pop()       只碰 d（最晚进来的）
队列（FIFO）  append →  [ a  b  c  d ]  → popleft()   只碰 a（最早进来的）
```

什么时候要「最晚的」：**嵌套**。括号、函数调用都是后开始的先结束，所以最近一个还没闭合的左括号一定在栈顶（20 的注释），
394 的栈就是手写的函数调用栈。什么时候要「最早的」：**按到达顺序**处理，BFS 里先进队的离起点近。

栈的几种用法（配对、求值、单调栈、上下文栈、辅助栈）见 [栈的几种用法](../paradigms/stack.md)，这页只讲结构本身。

## 1. Python 里用什么

| | 用 | 进 | 出 | 看一眼 |
|---|---|---|---|---|
| 栈 | `list` | `append(x)` | `pop()` | `a[-1]` |
| 队列 | `deque` | `append(x)` | `popleft()` | `q[0]` |

这几个操作都是 O(1)（list 尾部是均摊 O(1)）。拿 list 当队列、`pop(0)` 是 O(n)。
底层为什么是这样、完整的复杂度表见 [list.md](../python/list.md)、[deque.md](../python/deque.md)。

**空的时候不能看、不能弹**：空 list 的 `a[-1]` 和 `pop()`、空 deque 的 `popleft()` 都抛 `IndexError`，先判 `if stk`。
20 的第一个失败条件就是「栈空却来了右括号」；155 的 push 在栈空时没有 `minstk[-1]` 可比，要单独处理。

## 2. 换一个容器，BFS 就变成 DFS

迭代版的 BFS 和 DFS 是**同一份代码**，只差从哪一头取：

```python
def traverse(start, neighbors, use_stack):
    frontier = deque([start])
    seen = {start}
    order = []
    while frontier:
        if use_stack:
            cur = frontier.pop()         # 取最晚进来的：沿着刚发现的点往深处走
        else:
            cur = frontier.popleft()     # 取最早进来的：一圈一圈往外扩
        order.append(cur)
        for nxt in neighbors(cur):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return order
```

栈版的访问顺序和递归 DFS 不完全一样，只适合「走遍就行」的题（[dfs.md](../paradigms/dfs.md) §6）。

层序遍历时，这个区别落在**层内顺序**上（199 的 note）：

| frontier | 层内顺序 | 适合 |
|---|---|---|
| deque（FIFO） | 稳定的左 → 右 | 102、199（每层最后一个出队 = 最右边） |
| 栈，push 顺序固定 | 一层层叠加着打乱 | 没用 |
| 栈，push 顺序交替 | 左 → 右、右 → 左交替 | 103 锯齿 |

## 3. 栈能顺手存「截至这一格」的值，队列不能（155）

栈有个性质：一格**下面**的东西，在这一格被弹走之前一个都不会动。
所以每一格可以顺带存「从栈底到我为止」的聚合值，它在这一格活着的时候一直有效。155 Min Stack 就是这样：

```python
class MinStack:
    def __init__(self):
        self.lst = []
        self.minstk = []      # minstk[i] = lst[0..i] 里的最小值

    def push(self, value):
        if len(self.lst) > 0:
            self.minstk.append(min(self.minstk[-1], value))
        else:
            self.minstk.append(value)     # 空栈没有 minstk[-1] 可比
        self.lst.append(value)

    def pop(self):
        self.minstk.pop()
        return self.lst.pop()

    def top(self):
        return self.lst[-1]

    def getMin(self):
        return self.minstk[-1]
```

队列没有这个性质：最早进来的先走，存好的「从队首到我为止」最先失效的正是开头那部分。
所以 239 滑动窗口最大值没法照抄 155，要换成单调队列（§5）。

## 4. 两个栈拼一个队列：均摊 O(1)

（232 还没做，这里只记结构上的结论。）一个栈只管进，一个栈只管出；出的那个空了，就把进的那个整个倒过去，倒一遍顺序正好反过来：

```python
class MyQueue:
    def __init__(self):
        self.inbox = []       # 新来的压这里
        self.outbox = []      # 从这里出，栈顶 = 最早进来的

    def push(self, x):
        self.inbox.append(x)

    def pop(self):
        self._refill()
        return self.outbox.pop()

    def peek(self):
        self._refill()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox

    def _refill(self):
        if not self.outbox:   # 只有 outbox 空了才倒，否则新来的会压在老的上面先出去
            while self.inbox:
                x = self.inbox.pop()
                self.outbox.append(x)
```

单次 `pop` 可能要倒 n 个，但每个元素一生只会从 inbox 倒到 outbox **一次**，所以 n 次操作总共 O(n)，均摊 O(1)。
单调栈「每个下标进出各一次」也是这样算账的。

## 5. 单调栈 / 单调队列：再多维护一个「单调」

在栈 / 队列上再加一条规矩：从栈底到栈顶（队首到队尾）保持单调，新元素进来之前先把破坏单调的弹掉。结构上多出两件事：

- **相邻两格有含义**。单调递增栈里，一格下面那格就是它**左边第一个比它矮的**（中间比它高的早被它弹掉了）。
  84 的左边界就是这么「免费」拿到的：弹出 `top` 之后，**新的栈顶**才是左边界，不是 `top` 自己（`[2,1,2]` 踩过两次）。
- **每个元素进一次、出一次**，所以虽然循环里套着 `while`，总共还是 O(n)。

单调栈和单调队列在队尾的操作一模一样，区别在元素从哪离开、答案在哪（239 的 note）：

| | 单调栈 | 单调队列 |
|---|---|---|
| 元素怎么离开 | 只有一种：被新来的支配，从栈顶弹 | 两种：队尾弹被支配的，队首弹过期的 |
| 答案在哪 | **被弹出的**那个身上（739：谁把 j 弹走，谁就是 j 之后第一个更暖的天） | **留下来的队首**（239：窗口最大值） |
| 回答什么 | 每个元素左 / 右第一个更大 / 更小的 | 每个长度为 k 的窗口里的最值 |

队首也要弹，所以单调队列只能用 `deque`。具体写法见 [stack.md](../paradigms/stack.md) §3 和 [sliding-window.md](../paradigms/sliding-window.md)。
