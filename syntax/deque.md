# Python deque 语法坑

读法和 [str.md](str.md) 一样：**从头通读**当 checklist（写 BFS / 单调队列之前扫一眼），
或者在看板里 `🧠 复习 → 语法` 按 FSRS 抽卡。格式约定见 [dashboard/syntax.py](../dashboard/syntax.py)。

收录标准同样是**只收自己真栽过的**。deque 的 API 一共就那么几个，
值得做成卡的是那几个"不报错、只是悄悄错"或者"悄悄变慢"的地方。

---

## 想用队列做 BFS，deque 怎么建

---

```python
from collections import deque       # ← 在 collections 里，不是内置的

q = deque()                         # 空
q = deque([root])                   # 从可迭代初始化 ← BFS 起手最常用
q = deque(maxlen=5)                 # 定长，超了自动从另一端挤掉
```

四个进出，全是 **O(1)**：

```python
q.append(x)       # 右端进
q.appendleft(x)   # 左端进
q.pop()           # 右端出
q.popleft()       # 左端出
```

看两端不弹出用 `q[0]` / `q[-1]`，空判断直接 `while q:` / `if not q:`。
注意 `deque([root])` 里那层方括号别漏 —— `deque(root)` 会去迭代 `root`，
传个 TreeNode 进去直接 `TypeError: not iterable`。

栽过：102

## 这段 BFS，为什么出来的顺序是反的

```python
q = deque([root])
while q:
    node = q.pop()
    print(node.val)
    if node.left:  q.append(node.left)
    if node.right: q.append(node.right)
```

---

`q.pop()` 弹的是**右**端（和 list 一样），右进右出 = 栈 = 这段其实在做 **DFS**。
BFS 要的是**左出右进**：

```python
node = q.popleft()        # ✔
```

这个坑**不报错**，树小的时候答案甚至可能碰巧对，所以特别阴。记的时候别记"pop 还是 popleft"，
记**方向**：`append` 在右边加，那就得从**左边**拿，才是先进先出。

顺带，反过来也成立 —— 想要栈就大方用 list（`append` / `pop`），
list 的右端本来就是 O(1)，不需要 deque。

栽过：102、133、417

## BFS 用 list 当队列，哪里慢了

---

`list.pop(0)` 是 **O(n)** —— 弹掉头一个之后，后面每个元素都要往前挪一格。
整个 BFS 就从 O(V+E) 退化成 **O(V²)**，节点一多就 TLE。

```python
q = [root]
while q:
    node = q.pop(0)       # ✘ 每次 O(n)
```

deque 是双向链表式的实现，两端都 O(1)，所以 BFS 一律用它。
代价（换来的东西总要还）：

- **随机访问是 O(n)** —— `q[0]` / `q[-1]` 快，`q[len(q)//2]` 慢
- **不支持切片** —— `q[1:3]` 直接 `TypeError`，要切先 `list(q)`

反过来说，需要下标随机访问的场景就别用 deque。
两边都要 O(1) 的只有队列这一类。

栽过：102

## 分层 BFS，为什么内层不能写 while q

```python
while q:
    level = []
    while q:                       # ← 这里
        node = q.popleft()
        level.append(node.val)
        if node.left:  q.append(node.left)
        if node.right: q.append(node.right)
    res.append(level)
```

---

内层 `while q` 会**一直吃到队列空**，而循环体里还在往 q 里塞下一层 ——
结果是整棵树被塞进同一个 level，外层只转一圈。

要分层就得**先把这一层的个数拍下来**：

```python
while q:
    level = []
    for _ in range(len(q)):        # ✔ len(q) 只求值一次 = 进循环时这层的节点数
        node = q.popleft()
        level.append(node.val)
        if node.left:  q.append(node.left)
        if node.right: q.append(node.right)
    res.append(level)
```

关键是 `range(len(q))` 的 `len(q)` **只在进 for 的那一刻算一次**，之后 q 怎么变都不影响循环次数。
换成 `while i < len(q)` 那种每轮重算的写法，同样会追着新塞进去的节点跑。

一句话记法：**外层 while 管层，内层 for 管这一层的人头**，
所以分层 BFS 天然是两重循环，不分层（只要遍历顺序）才是一重。

栽过：102
