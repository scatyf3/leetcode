---
title: 递归
status: draft
order: 18
alias: []
related: [/paradigms/dfs, /structures/tree, /structures/linked-list]
---

# 递归

**先写下这个函数「答应」返回什么，然后假设它对更小的输入已经做对了。** 自己这一层只干两件事：
最小的情况直接回答（base case）；其余的交给更小的自己，再把结果拼起来。不用、也不该在脑子里把调用一层层展开。

```
depth(node) = max(depth(node.left), depth(node.right)) + 1     # 104
                  └──────── 假设已经对了 ────────┘    └ 我这层只做这一步
depth(None) = 0                                                # base case
```

树上的递归（信息往下传还是往上交、返回值 ≠ 答案、`nonlocal`）都在 [dfs.md](dfs.md) §1，这页讲树以外也成立的三件事：
契约怎么定、问题有没有变小、递归栈里存了什么。

## 1. 难的是定契约

「返回什么」定对了，代码几乎是自己写出来的；定错了，怎么补都别扭。

- 124 第一遍想的是「对每个节点各调一次 dfs，各自找最长的左路径和右路径」。契约定成
  「`dfs(node)` 返回以 node 为顶、只往一侧向下的最大和」之后，全局答案在每个节点顺手更新就行（124 的 note，写法见 dfs.md）。
- 110 先确认题目说的是「**每个**节点左右高度差 ≤ 1」（第一遍理解错了），之后契约就是 104 的「返回高度」，每个节点顺手比一下左右。

## 2. 每次递归，问题必须严格变小（148）

148 归并排序链表：base case 是「空或只有一个节点」，其余切两半、各自递归、再合并。sol.py：

```python
def sortList(head):
    # 1. 递归出口：空链表或只有一个节点，本身就是有序的
    if head is None or head.next is None:
        return head

    # 2. 快慢指针找中点（fast 从 head.next 出发）
    slow, fast = head, head.next
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

    # 3. 从中点切成两半：先存右半的头，再断开
    mid = slow.next
    slow.next = None

    # 4. 两半分别排序
    left = sortList(head)
    right = sortList(mid)

    # 5. 合并两个有序链表（21）
    dummy = ListNode(0)
    cur = dummy
    while left and right:
        if left.val < right.val:
            cur.next = left
            left = left.next
        else:
            cur.next = right
            right = right.next
        cur = cur.next
    cur.next = left if left else right   # 剩下没合并完的一段整个接上
    return dummy.next
```

`fast` 为什么从 `head.next` 出发：n = 2 时如果写 `fast = head`，slow 会走到第二个节点，`mid = slow.next = None`，
左半还是原来那两个节点 —— 问题没有变小，`sortList(head)` 一直调自己，直到 `RecursionError`。
`fast = head.next` 时 slow 停在第一个，2 个才切得成 1 + 1（148 的 note：「n=2 才切得开」）。

> 写完 base case，拿「比 base case 大一点」的输入（这里是 n = 2）代进去走一遍，看问题有没有真的变小。

链表那一侧的坑（先存再断、`left or right` 收尾）见 [linked-list.md](../structures/linked-list.md) 原语 3。

## 3. 递归栈里存了什么，决定能不能改成循环（206）

206 的 note 问过：为什么树非得递归，链表就不用？判据不是「有没有分叉」，而是**递归栈里到底存了什么**。它只可能存两样：

| 栈里存的 | 例子 | 能不能塌成循环 |
|---|---|---|
| 还没走的分支（待办） | 树：走完左子树还得回来走右子树 | 不能直接塌，要自己维护一个栈 |
| 回来之后还要用的现场 | 后序：要先拿到后面的结果才能处理当前（104、124） | 同上 |
| 都没有：边走边算，走到底答案就有了 | 206 尾递归版 | **能**，O(1) 空间 |

206 正好两种递归都写得出来，分别落在表的后两行：

```python
# sol.py：尾递归，翻转在「递下去」的路上做完
def reverseList(head):
    def dfs(prev, curr):
        if curr is None:      # end of list, prev is the new head
            return prev
        nxt = curr.next       # save it, next line overwrites it
        curr.next = prev      # flip this one edge
        return dfs(curr, nxt) # pass the new head straight up
    return dfs(None, head)
```

```python
# sol2.py：后序，先把后半截整个翻好，在「归上来」的路上接回自己
def reverseList(head):
    if head is None or head.next is None:
        return head              # 空表或只剩一个，它自己就是新头
    p = reverseList(head.next)   # 先把后半截整个翻好，p 是新头
    head.next.next = head        # 此刻 head.next 是后半截翻转后的尾巴，让它指向自己
    head.next = None             # 断开旧的正向指针，否则成环
    return p                     # 新头原样往上传
```

- **尾递归版**：两个参数 `(prev, curr)` 就是迭代版循环里那两个变量，`return dfs(curr, nxt)` 就是「进入下一轮」。
  回来的路上什么都不做，栈里没有要等的东西 —— 它是循环换了层皮。
- **后序版**：`head.next.next = head` 要用的是**递下去之前**的那个 `head`，它必须在栈上等着，这就是表里的「现场」。

迭代版，以及为什么是 prev / curr 两个真状态、nxt 只是临时变量，见 [linked-list.md](../structures/linked-list.md) 原语 3。

## 4. Python 里的递归

- **默认深度上限是 1000**（`sys.getrecursionlimit()`）。206 的两种递归深度都等于链表长度，链表一长就 `RecursionError`，
  所以 206 推荐迭代写法（206 的 note）；148 每层切一半，深度只有 log n。
- **CPython 不做尾调用优化**：尾递归版照样每层占一帧，深度和后序版一样是 O(n)。
  「尾递归 = 循环」说的是你可以**手动**把它改成循环，不是解释器会替你改。
- 网格这种可能很深的，改显式栈或 BFS，见 [dfs.md](dfs.md) §6。
