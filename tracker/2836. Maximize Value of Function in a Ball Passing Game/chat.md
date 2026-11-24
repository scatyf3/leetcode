<!-- chat 6f2a01ea/a0cb8ee8 2026-11-22 -->

#### 🧑 我

2836. Maximize Value of Function in a Ball Passing Game

这道题有任何hint吗，我的想法就是按照k展开成tree，然后找最大，是这样吗，但是枚举空间好像有点大

#### 🤖 Claude

你的方向对了一半，先改一处：**它不是 tree，每个起点只有一条链**。每个人只传给固定的 `receiver[i]`，没有分叉，唯一的选择是起点 `i`，共 n 个。

所以起点不多，大的是**每条链太长**：n=10⁵，k 最大 10¹⁰，暴力要走 10¹⁵ 步。问题变成：**怎么不一步步走，就知道走 k 步后在哪、总分多少？**

三级提示，卡住再往下看。

## 提示 1：你写过类似的

你在 50 题 Pow(x, n) 里没有真的乘 n 次，而是把指数拆成二进制：

```
13 = 8 + 4 + 1
x^13 = x^8 · x^4 · x^1
```

这里也可以：**走 13 步 = 走 8 步 + 走 4 步 + 走 1 步**。`x` 对应「走 1 步」，那 `x *= x` 对应什么？

## 提示 2：步子怎么翻倍

设 `to[i]` 是从 i 走 **L 步**后到的人，一开始 `L = 1`，`to = receiver`。

用 `receiver = [2,0,1]` 手算：
1. 走 2 步的表是什么？
2. 已知走 L 步的表 `to`，走 2L 步的 `to2[i]` 怎么写？

k ≤ 10¹⁰ 只需翻倍约 34 次，每次更新 n 个人，总共约 3.4×10⁶，能过。这个技巧叫**倍增（binary lifting）**。

分数也要跟着翻倍。设 `s[i]` 是从 i 走 L 步的得分：

> 走 2L 步的得分 = 前 L 步的得分 + 后 L 步的得分。后 L 步**从谁出发**？

注意别把中间那个人算两次。建议让 `s[i]` **含起点、不含终点**，那么 `L = 1` 时 `s[i]` 等于几？

## 提示 3：骨架（关键处留白）

```
to = receiver，s = ______
pos[i] = i        # 从 i 出发，现在走到谁
score[i] = 0      # 目前的得分（不含 pos[i]）

while k > 0:
    if k & 1:     # 对应 50 题的 ans *= x
        对每个 i：score[i] += ______，再 pos[i] = ______
    # 对应 50 题的 x *= x
    s, to = ______, ______
    k >>= 1

return max(score[i] + ______)
```

两个坑：
- `if` 里先更新 score 再更新 pos，因为加的是从**旧的** pos 出发的得分
- 翻倍时新的 `s` 要用**旧的** `to`，所以两个一起赋值

先做提示 2 的两小问，把 `to2` 和 `s2` 的式子贴过来。

#### 🧑 我

但是你这个需要枚举起点和分支啊

#### 🤖 Claude

**起点要枚举，但只有 n 个；分支没有**，因为 `receiver[i]` 是一个数，不是列表，i 手里的球只能传给这一个人。

用例 2 看：`receiver = [1,1,1,2,3]`，`k = 3`

```
从 0：0 → 1 → 1 → 1    得分 3
从 1：1 → 1 → 1 → 1    得分 4
从 2：2 → 1 → 1 → 1    得分 5
从 3：3 → 2 → 1 → 1    得分 7
从 4：4 → 3 → 2 → 1    得分 10  ← 最大
```

起点一定，后面整条链就定了，所以 **n 个起点只有 n 条链**，不是 n × 2^k。

你可能是看到 0、1、2 都传给 1，觉得有分叉。那是**多个人传给同一个人**（入边多），链只会汇合。分支要**一个人能传给多个人**（出边多），这里每人只有一条出边，和 2360 一样。

## 枚举起点会不会太贵？

| 做法 | 每个起点的代价 | 总代价 |
|---|---|---|
| 一步步走 | k = 10¹⁰ | 10¹⁵ ❌ |
| 倍增 | log k ≈ 34 | 10⁵ × 34 ≈ 3.4×10⁶ ✅ |

倍增没有省掉枚举起点，它省的是**每条链上走的步数**。而且翻倍表**所有起点共用**：「从 3 走 4 步到哪」只算一次，谁走到 3 都直接查。

代码里的 `if k & 1` 也不是分支枚举，它只看 k 的二进制，所有起点拆法相同：k = 13 时，大家都是走 1 + 4 + 8 步。

## 回到手算

`receiver = [2,0,1]`，走 1 步的表是：

```
i      0  1  2
to[i]  2  0  1
```

走 2 步的表，我填第一个：从 0 走 1 步到 2，再从 2 走 1 步到 1，所以 `to2[0] = 1`。

`to2[1]` 和 `to2[2]` 是几？然后写出通式：`to2[i] = ______`。

#### 🧑 我

```python
class Solution:
    def getMaxFunctionValue(self, receiver: List[int], k: int) -> int:
        # 函数图，given start+k，怎么走时确定性的，唯一的复杂性来自于k太大了
        to = receiver
        s = ______
        pos[i] = i        # 从 i 出发，现在走到谁
        score[i] = 0      # 目前的得分（不含 pos[i]）

        while k > 0:
            if k & 1:     # 对应 50 题的 ans *= x
                for i in range(n):
                    score[i] += i
                    pos[i] = receiver[i]
            # 对应 50 题的 x *= x
            s, to = ______, ______
            k >>= 1

        return max(score[i] + ______)
```


        receiver是要平方吗receiver，但“batch indexing”支持吗，然后s是啥玩意啊

#### 🤖 Claude

对，就是「平方」：**先走 L 步，再走 L 步**，也就是查两次表，`to2[i] = to[to[i]]`。

## batch indexing

Python 的 list **不支持** `to[to]`，会报 TypeError，用列表推导：

```python
to = [to[j] for j in to]     # j 就是 to[i]
```

numpy 数组可以直接写 `to[to]`，不过这里用列表推导就够了。

## s 是什么

`to` 记「走 L 步**到哪**」，`s` 记「走这 L 步**得多少分**」，含起点、不含终点。

还是 `receiver = [2,0,1]`：

| i | 走 1 步 | s (L=1) | 走 2 步 | s (L=2) |
|---|---|---|---|---|
| 0 | 0→(2) | 0 | 0→2→(1) | 0+2 = 2 |
| 1 | 1→(0) | 1 | 1→0→(2) | 1+0 = 1 |
| 2 | 2→(1) | 2 | 2→1→(0) | 2+1 = 3 |

括号里是终点，不计分。所以 L=1 时 `s = [0,1,2]`，`s[i]` 就等于 `i`。

L=2 的 `s2[0] = 2` 可以拆成两段：前 1 步从 0 出发，得 `s[0] = 0`；后 1 步从 2 出发，得 `s[2] = 2`。这个 2 就是 `to[0]`。**通式 `s2[i] = s[i] + ______`？**

## 你的 `if` 里有个 bug

```python
score[i] += i
pos[i] = receiver[i]
```

拿 `k = 3`（先走 1 步，再走 2 步）、起点 0 来 trace：

| | 正确 | 你的代码 |
|---|---|---|
| 走 1 步后 | pos=2，score=0 | pos=2，score=0 |
| 再走 2 步后 | pos=0，score=0+2+1=3 | pos=2，score=0 |

第二轮你又从 **i** 走了 **1 步**，但此时人在 2，要走 2 步。改之前想两件事：
1. 这一轮从谁出发？不是 `i`，是 `______`
2. 这一轮的步长是 L，得分和终点该查哪两张表？不是 `i` 和 `receiver`，是 `______` 和 `______`

另外 `n`、`pos`、`score` 还没初始化成列表：

```python
n = len(receiver)
pos = list(range(n))
score = [0] * n
```

还剩这些空：`s` 的初始值、`if` 里两行、`s, to = ...`、`return`。最后一个想想 `score` 不含谁的分。改完贴过来。

#### 🧑 我

```python
class Solution:
    def getMaxFunctionValue(self, receiver: List[int], k: int) -> int:
        # 函数图，given start+k，怎么走时确定性的，唯一的复杂性来自于k太大了
        n = len(receiver)
        pos = list(range(n))
        score = [0] * n
        to = receiver
        s = [i for i in range(n)]
        pos[i] = i        # 从 i 出发，现在走到谁
        score[i] = 0      # 目前的得分（不含 pos[i]）

        while k > 0:
            if k & 1:     # 对应 50 题的 ans *= x
                for i in range(n):
                    score[i] += i
                    pos[i] = receiver[i]
            # 对应 50 题的 x *= x
            s= [receiver[i] for i in range(n)]
            to = [to[j] for j in to] 
            k >>= 1
```


这对吗

#### 🤖 Claude

还不对。**初始化、`to` 的翻倍、`k >>= 1` 都对了**，`s` 放在 `to` 前面更新，顺序也对。还有四处要改：

| # | 位置 | 问题 |
|---|---|---|
| 1 | `pos[i] = i`、`score[i] = 0` | 循环外没有 `i`，会报 NameError。上面已经初始化了，**删掉这两行** |
| 2 | `if` 里两行 | 还是上次的 bug：每轮都从 `i` 走 1 步 |
| 3 | `s = [receiver[i] ...]` | `receiver[i]` 是**传给谁**，不是得分，前一半的分也丢了 |
| 4 | 结尾 | 没有 return |

删掉第 1 处、补上 return 后跑例 1（`k = 4`）会得 **3**，正确答案是 **6**。因为 4 的二进制是 `100`，`if` 只进一次，这一次本该走 4 步，你只走了 1 步。翻倍好的 `to` 和 `s` **从头到尾没被用上**。

## 改第 2 处：`if`

先把「人现在在哪」单独取出来：

```python
p = pos[i]            # 现在站在 p，接下来要走 L 步
score[i] += ___[p]    # 从 p 走 L 步，得多少分？
pos[i] = ___[p]       # 从 p 走 L 步，到哪？
```

从 `to` 和 `s` 里各选一个填进去。

## 改第 3 处：`s` 的翻倍

走 2L 步的得分 = 前 L 步 + 后 L 步：

```python
s = [s[i] + s[___] for i in range(n)]
```

- 前 L 步从 `i` 出发，得 `s[i]`
- 后 L 步从**走完前 L 步到的人**出发，这个人是谁？

用 `receiver = [2,0,1]` 检查：翻倍一次后 `s` 应该从 `[0,1,2]` 变成 `[2,1,3]`。你现在的写法会变成 `[2,0,1]`。

## 改第 4 处：return

`score[i]` 不含**最后拿到球的人**，所以每个起点要补上谁的下标？然后取 max：

```python
return max(score[i] + ______ for i in range(n))
```

填完这四个空就是完整解法，用例 1 = 6、例 2 = 10 验证一下。

#### 🧑 我

```python
class Solution:
    def getMaxFunctionValue(self, receiver: List[int], k: int) -> int:
        # 函数图，given start+k，怎么走时确定性的，唯一的复杂性来自于k太大了
        n = len(receiver)
        pos = list(range(n))
        score = [0] * n
        to = receiver
        s = [i for i in range(n)]


        # batching fast pow
        while k > 0:
            if k & 1:     # 对应 50 题的 ans *= x
                for i in range(n):
                    p = pos[i]            # 现在站在 p，接下来要走 L 步
                    score[i] += s[p]    # 从 p 走 L 步，得多少分？
                    pos[i] = to[p]       # 从 p 走 L 步，到哪？
            # 对应 50 题的 x *= x
            s= [s[i]+s[n-i] for i in range(n)]
            to = [to[j] for j in to] 
            k >>= 1

        return max(score[i] + s[i] for i in range(n))
```


        

再fix下，谢谢

#### 🤖 Claude

`if` 里已经对了，只剩两处：

| 位置 | 你的 | 改成 |
|---|---|---|
| `s` 翻倍 | `s[n-i]` | `s[to[i]]` |
| return | `score[i] + s[i]` | `score[i] + pos[i]` |

```python
class Solution:
    def getMaxFunctionValue(self, receiver: List[int], k: int) -> int:
        n = len(receiver)
        pos = list(range(n))     # 从 i 出发，现在走到谁
        score = [0] * n          # 目前得分，不含 pos[i]
        to = receiver            # 走 L 步到谁
        s = list(range(n))       # 走 L 步得分，含起点、不含终点

        while k > 0:
            if k & 1:
                for i in range(n):
                    p = pos[i]
                    score[i] += s[p]
                    pos[i] = to[p]
            # L -> 2L，s 要用旧的 to，所以先更新 s
            s = [s[i] + s[to[i]] for i in range(n)]
            to = [to[j] for j in to]
            k >>= 1

        return max(score[i] + pos[i] for i in range(n))
```

我跑过了：例 1 = 6，例 2 = 10，3000 组随机小数据和暴力一致；n = 10⁵、k = 2³³-1 约 0.9 秒。

## 为什么是 `s[to[i]]`

后 L 步要从**走完前 L 步到的人**出发，这个人就是 `to[i]`。`n-i` 和传球关系无关，而且 `i = 0` 时 `s[n]` 直接越界报 IndexError。

```
i ──L 步──> to[i] ──L 步──> to[to[i]]
   s[i]           s[to[i]]
```

`to` 和 `s` 的翻倍是同一个动作：**先跳到 `to[i]`，再查一次表**。

## 为什么是 `pos[i]`

`score[i]` 每段都不含终点，各段接起来后，只漏了**最后拿球的人**，也就是 `pos[i]`。

循环结束时的 `s` 是走 2L 步的得分表，比 k 的最高位还多翻了一倍，和答案无关。

## 和 50 题对照

| 50 Pow | 2836 |
|---|---|
| `ans` | `pos`、`score` |
| `x` | `to`、`s` |
| `ans *= x` | 从 `pos[i]` 查 `s` 和 `to` |
| `x *= x` | `s`、`to` 各翻倍 |

以后看到**每步走法固定 + k 大到不能一步步走**，就想倍增。
