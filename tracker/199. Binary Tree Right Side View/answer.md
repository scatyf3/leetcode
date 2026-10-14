层序 BFS（deque，孩子按左→右入队），每层**最后一个**出队的节点就是这一层从右边看到的，记下它的 `val`。

⚠ frontier 用 deque（FIFO）不用 stack：stack 会把层内顺序打乱，「最后一个」就不是最右边。
