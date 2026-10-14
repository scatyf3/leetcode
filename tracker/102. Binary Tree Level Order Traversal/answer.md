BFS，每层开头先取 `len(q)`，`for _ in range(len(q))` 只弹这一层的节点，孩子 append 到队尾留给下一层（等价于 cur / next 两个队列来回换）。

⚠ 出队用 `deque.popleft()`；孩子先判 `None` 再入队，否则下一轮才炸。
