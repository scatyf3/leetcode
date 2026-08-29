# 链表三件套模板:找中点 / 反转 / 交替合并

适用:LC 141 / 143 / 148 / 19 / 206 / 21 / 234 / 876。

核心前提:链表**只能向前走**,而且**每次写 `node.next` 都是破坏性的**——它覆盖掉的正是你唯一通往后面的路。所有模板都是围绕这两件事设计的。

大部分链表题 = 从下面三块里挑两块拼起来。分开背没用,**要背的是它们之间的接口约定**。

---

## 1. 快慢指针找中点:先决定要左中点还是右中点

这是全套里最容易写错的一块,因为它有两个都"对"的版本,落点差一格。

### 只记一个循环形状,一个旋钮

三种写法其实是一个模板。**把提前量放在初值里,条件永远不变**:

```python
slow, fast = head, head          # ← 落右中点   (head 可以是 None)
slow, fast = head, head.next     # ← 落左中点   (head 必须非空)
while fast and fast.next:        # 条件永远是这一句
    slow, fast = slow.next, fast.next.next
```


**记忆法:fast 的提前量决定 slow 的落点。** fast 每轮走 2、slow 走 1,fast 提前一步起跑,slow 就往左退一格。同一个母题:LC 19 删倒数第 k 个,让 fast 先走 k 步,slow 就停在倒数第 k+1 个。**快慢指针的落点 = 提前量的函数**,不是玄学。

1. 这里的mindset是用偶数列表来举例子看
2. 左中点严格比右中点好

---

## 2. 反转:条件是 `curr`,返回 `prev`

```python
def reverse(head):
    prev, curr = None, head
    while curr is not None:      # 不是 while curr.next
        nxt = curr.next          # 抢救:下一行就要把它覆盖掉
        curr.next = prev
        prev = curr
        curr = nxt
    return prev                  # 不是 curr —— 此刻 curr 已是 None
```

两个高频错误是**同一个 off-by-one 的两面**:

| 写错 | 后果 |
|------|------|
| `while curr.next` | 最后一个节点没进循环,它那条边没翻 → **整条链只剩尾节点**,前面全丢 |
| `return curr` | curr 退出时恒为 None → 返回空链表 |

判据:循环退出时 `curr` 停在**第一个不合法的位置**(None),所以"最后一个合法节点"是 `prev`。参见 [off-by-one-checklist.md](off-by-one-checklist.md) 的同名小节。

**契约(很重要,调用方靠它省特判)**:
- `reverse(None)` → `None`,天然处理空链表
- 返回新头 = 原来的尾
- **副作用:原来的头会变成新的尾,它的 `next` 被置成 `None`** —— 也就是说 reverse 自己就完成了一半的断开工作

为什么不用三元组赋值 `head.next, prev, head = prev, head, head.next`:见 [206 的笔记](../206.%20Reverse%20Linked%20List/note.md),它没消灭 tmp,只是把 tmp 藏进了元组,还更容易写错。

---

## 3. 交替合并:循环条件只看短的那条

```python
def merge_alt(first, second):
    """first=[1,2,3] second=[5,4] -> 1->5->2->4->3;要求 len(first) >= len(second)"""
    while second:
        n1, n2 = first.next, second.next    # 两个都要先存, 下面两行都是破坏性写入
        first.next = second
        second.next = n1
        first, second = n1, n2
```

**为什么只判 `second` 就够**:设前半长 f、后半长 s,每轮各消耗一个。`second` 非空 ⟹ 已消耗 k < s ≤ f ⟹ `first` 必非空。所以 `first` 永远不用判——**前提是 f ≥ s**。

这就把第 1 块和第 3 块串起来了:

```
切在左中点  ⟹  前半 ≥ 后半  ⟹  merge 只需 while second  ⟹  零特判
```

反过来,如果第 1 块选了右中点,两半变成前半 ≤ 后半,这里的循环条件就得改判 `first`,并且末尾还得手动把 second 的剩余接上——**一个选择错位,下游多两个特判**。这是链表题里典型的「前一步的约定决定后一步能省多少代码」。

### 对照:插入式写法(能用,但特判多)

```python
prev, curr, node = first, first.next, second
while node:
    prev.next = node
    nxt = node.next
    node.next = curr
    node = nxt
    prev = curr
    curr = curr.next if curr is not None else None   # ← 等长时 curr 已经是 None
```

它需要 3 个游标 + 2 个前置特判(`second is None`、`first.next is None`)+ 1 个 None 保护;`merge_alt` 一个都不要。原因是插入式在循环里**同时维护 prev 和 curr 两个前半段指针**,而它俩可以互推(`curr == prev.next`),属于第 206 篇里说的「能算出来的东西不是状态」。

---

## 4. 拼装:LC 143 全貌

```python
class Solution:
    def reorderList(self, head):
        if head is None:
            return
        # 1. 切在左中点: fast 提前一步起跑, slow 停在前半段的尾
        slow, fast = head, head.next
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
        # 2. 反转后半段 (reverse(None) -> None, 单节点时天然是 no-op)
        second = reverse(slow.next)
        slow.next = None
        # 3. 前半 >= 后半, 所以只判 second
        merge_alt(head, second)
```

`slow.next = None` 和 `reverse(...)` 的**顺序无所谓**:reverse 会把原 `slow.next` 那个节点的 `next` 置成 None,两半已经断了;这句只是把 slow 这侧的指针也清干净。留着,别删——不留的话 `slow.next` 指向的是反转后后半段的**尾**,直接成环。

`fast` 用完就该丢:它只是配速器,停在末尾附近,**不是后半段的头**(只有 n=3/4 时恰好相等,这个巧合坑过一次,见 [143 的复盘](../143.%20Reorder%20List/note.md))。

---

## 5. 组合表:哪题用哪几块

| 题 | 找中点 | 反转 | 合并 | 备注 |
|----|--------|------|------|------|
| 141 环形链表 | 只用配速,不取中点 | | | 判 `slow is fast` |
| 876 中间节点 | **A 右中点** | | | 题目明确要靠右那个 |
| 206 反转链表 | | ✓ | | |
| 21 合并有序链表 | | | 归并式(非交替) | 用 dummy 头 |
| **143 重排链表** | **B/C 左中点** | ✓ | 交替 | 三块全用 |
| 234 回文链表 | B/C | ✓ | 用比较代替合并 | |
| 148 排序链表 | **B/C 左中点** | | 归并 | 递归,必须能切断 |
| 19 删倒数第 k | 提前量 = k | | | 同一个"提前量"母题 |

另外一块没在这里展开但同样高频的:**dummy 哨兵节点**。凡是**头节点可能被删除或被换掉**的题(19 / 21 / 203 / 82),开头 `dummy = ListNode(0, head)`、结尾 `return dummy.next`,能消掉全部"如果删的是头怎么办"特判。143 不需要,因为头节点永远还是头。

---

## 6. 自测脚手架(链表题固定用这套)

```python
def mk(vals):
    h = None
    for v in reversed(vals):
        h = ListNode(v, h)
    return h

def dump(h, limit=10**5):        # limit 必须有: 一旦成环, 没它就无限打印
    o = []
    while h and len(o) < limit:
        o.append(h.val); h = h.next
    return o
```

**必跑的退化用例:n = 0, 1, 2, 3, 4, 5, 6, 7。**

- n=0/1:while 一轮不跑,指针还在原地
- n=2:最短的"两半等长"
- n=3/4:唯一 `fast == slow.next` 的巧合区,**只测这两个会给你虚假的信心**
- n=5:第一个能暴露"错把 fast 当后半段头"的用例
- n=6:第一个既是偶数又跑 ≥2 轮的

**分函数对拍,不要整体跑。** 每块单独喂正确输入验证:

```python
assert dump(reverse(mk([3,4]))) == [4,3]          # 抓 while curr.next / return curr
h = mk([1,2,3]); merge_alt(h, mk([5,4])); assert dump(h) == [1,5,2,4,3]   # 奇数
h = mk([1,2]);   merge_alt(h, mk([4,3])); assert dump(h) == [1,4,2,3]     # 偶数等长
```

整体跑的话,几个 bug 会互相掩盖(前一块丢节点 → 后一块的边界分支根本走不到),症状少不等于 bug 少。完整案例见 [143 的复盘](../143.%20Reorder%20List/note.md)。

---

## 速记

1. **找中点先问:我要头还是要尾?** 要切断就用左中点(`fast=head.next` 提前一步),`slow.next` 直接切;
   循环条件永远是 `while fast and fast.next`,唯一的旋钮是 fast 的起点
2. **左右中点在奇数长度时是同一个节点**,`L.next` 不是无脑能用的;奇偶看 fast 的退出姿势免费拿
3. **反转:条件 `curr`,返回 `prev`**;`reverse(None)` 返回 None,调用方不用特判
4. **交替合并只判短的那条**;前半 ≥ 后半这个不变式由第 1 步保证
5. 破坏性写入前先存 `nxt`——**能被覆盖的路,写之前抢救一行**
6. 头可能被删 → 上 dummy 哨兵
7. 退化用例跑到 n=7,分块对拍,`dump` 一定带 limit
