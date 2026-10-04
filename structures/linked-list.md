# Linked List 通用 trick

链表题拆开看就两层:

- **原语层**(这篇):dummy、删除靠前驱、尾插建链、先存再写、双向链表的四根指针 —— 几乎每题都在用
- **套路层**:找中点 / 反转 / 交替合并三件套,单独写在 [linked-list-template.md](../notes/linked-list-template.md),这里不重复

> 两条底层事实,所有 trick 都从这里长出来:
> 1. **单链表只能向前走** —— 走过去就回不来,所以要"往回看"的东西必须提前存(prev、前驱、dummy)
> 2. **写 `node.next` 是破坏性的** —— 覆盖掉的正是你唯一通往后面的路,所以写之前先抢救一行

---

### 原语 1:dummy 哨兵 —— 头可能变,就上哨兵

```python
dummy = ListNode(0, head)
...
return dummy.next          # 不是 head: 头被删 / 被换时 head 已经是野的
```

判据只有一句:**头节点会不会被删掉或换掉?**

| 会 → 上 dummy | 不会 → 不用 |
|---|---|
| 19 删倒数第 n(n == L 删的就是头) | 83 去重(头永远留下,单游标 `cur` 就够) |
| 203 删指定值(头可能就是要删的) | 143 重排(头永远是头) |
| 21 / 148 归并、2 两数相加(新链的头还不存在) | 141 / 142 判环(只读不写) |

dummy 的本质:**给"头的前驱"造一个实体**。19 的推导里待删节点前驱是 idx L-n-1,删头时变成 idx -1 —— dummy 就是那个 -1。

### 原语 2:删除靠前驱 —— 删了不动,没删才走

单链表删 `cur` 必须改 `prev.next`,所以游标得停在**待删节点的前一个**。

```python
prev, cur = dummy, head
while cur:
    if 要删 cur:
        prev.next = cur.next      # prev 不动!
    else:
        prev = cur
    cur = prev.next               # 两个分支统一从 prev 重新取 cur
```

**关键不对称:删除分支里 prev 不前进。** 删完之后 `prev.next` 已经是新的下一个,下一轮要接着检查它。
203 踩过:写成 `cur = prev.next.next`,等于删完又多跳一步,连续两个要删的节点会漏掉第二个。

只比相邻的(83)可以省掉 prev:`while cur and cur.next: if cur.val == cur.next.val: cur.next = cur.next.next else: cur = cur.next` —— 这里"前驱"就是 `cur` 自己。

### 原语 3:尾插建新链 —— dummy + tail

```python
dummy = tail = ListNode()
while ...:
    tail.next = 某个节点
    tail = tail.next
return dummy.next
```

21 / 148 的归并、2 的逐位相加都是这个形状。归并的收尾 **`tail.next = l1 or l2`**:循环退出时至少一条已空,剩下那条整段有序,直接接上(148 踩过写成 `right.next`,跳过一个节点还会在 None 上炸)。

### 原语 4:先存再写

任何 `x.next = ...` 之前问一句:**`x.next` 原来指向的东西后面还要不要?** 要就先存进 `nxt`。

- 206 反转:`nxt = curr.next` 必须在 `curr.next = prev` 之前
- 143 交替合并:`n1, n2 = first.next, second.next` 两个都要先存
- 148 切半:`mid = slow.next` 必须在 `slow.next = None` 之前(踩过写成 `mid = slow`,右半整段丢失还自环)

为什么是 prev+curr 两个真状态、nxt 只是 tmp,见 [206 的笔记](../206.%20Reverse%20Linked%20List/note.md)。

### 节点比身份,不比值

- 判相遇 / 判同一节点用 `is`(141、142):两个节点 val 相同不代表是同一个
- 哈希表的 key 用**节点本身**而不是 val(138):val 可重复,节点对象是唯一的
- `is not` 是一个独立的二元运算符,不是 `is (not x)`(21 的笔记)

---

### 双向链表:一次改动 = 四根指针

146 LRU 的全部难点都在这里。哈希表负责 O(1) 定位,双向链表负责 O(1) 挪位置和淘汰(见 [hash-table.md](hash-table.md))。

**头尾都放哨兵**,真实节点永远夹在 `head` 和 `tail` 之间,所有 `if x is not None` 都能删掉:

```python
def unlink(node):                 # 摘下: 2 根
    node.prev.next = node.next
    node.next.prev = node.prev

def push_front(node):             # 插到 head 后: 4 根
    node.prev, node.next = head, head.next   # 先接好 node 自己的两根
    node.prev.next = node                    # 剩下两根都经由 node 去找邻居,
    node.next.prev = node                    # 顺序就无所谓了
```

先接自己、再让邻居指回来:这样后两行不依赖 `head.next` 的旧值,写反顺序也不会错。

LRU 只需要这两个原语:`get` = unlink + push_front;`put` 新 key = push_front(满了再 unlink `tail.prev`);`put` 已有 key = 改 val + unlink + push_front。

146 pass 2 踩过的三个坑,全是"只改了一个方向":

| 漏掉的 | 后果 |
|---|---|
| 删尾时没写 `tail_node.prev.next = tail` | 正向链还连着被删节点 |
| 挪到队头时没写 `prev_head.prev = node` | 反向链断,下次删尾删错 |
| `put` 已有 key 又新建了一个节点 | 旧节点留在链里,被淘汰时把新节点的 map 项删掉 |

> 自检:每个原语写完,数一下改了几根指针。摘下 2 根,插入 4 根,少一根就是 bug。
> 节点里要**存 key**:淘汰尾节点时得靠它 `del self.mp[node.key]`。

### 链表 = 函数:看到 `i → f(i)` 就想到链表

- **138 克隆带 random 的链表**:本质是图的克隆。两趟,第一趟建 `原节点 → 新节点` 的表(构造映射 f),第二趟查表连 `next` / `random`(让 f 保边)。f(v) 可能指向还没建的节点,所以必须先建完再连。表还顺带"保共享":多个 random 指向同一个 w,新图里也得是同一个 f(w)。同一套思路用在 133 Clone Graph
- **287 找重复数**:把 `i → nums[i]` 看成每个点出度为 1 的链表。下标 0 没有入边(值域是 1..n),所以从 0 出发一定走进环,**重复的值就是环入口** —— 直接套 142 的 Floyd。这题目前用值域二分做的(O(n log n)),Floyd 是 O(n) 的那条路

---

### 题型地图

| 题 | 归类 | 用到 | 一句话思路 |
|---|---|---|---|
| [206](../206.%20Reverse%20Linked%20List/) 反转 | 三件套·反转 | 先存再写 | prev / curr 是切口两侧,nxt 是 tmp;条件 `curr`,返回 `prev` |
| [21](../21.%20Merge%20Two%20Sorted%20Lists/) 合并两有序 | 归并 | dummy + 尾插 | 比较后尾插,收尾 `tail.next = l1 or l2` |
| [23](../23.%20Merge%20k%20Sorted%20Lists/) 合并 k 个 | 归并 + 堆 | 尾插 | 堆里只放 k 个当前头,元组塞下标破平局,O(N log k)(见 [heap.md](heap.md)) |
| [141](../141.%20Linked%20List%20Cycle/) 判环 | 快慢指针 | `is` | 一步 / 两步,`slow is fast` 即有环 |
| [142](../142.%20Linked%20List%20Cycle%20II/) 环入口 | 快慢指针 | | 同起点 head;相遇后一个回 head,同速走,再相遇即入口(a = c + (k-1)(b+c)) |
| [19](../19.%20Remove%20Nth%20Node%20From%20End%20of%20List/) 删倒数第 n | 快慢指针·提前量 | dummy + 删前驱 | 从 dummy 出发,fast 精确先走 n 步(用 `range`),同步走到 fast 是尾,slow 即前驱 |
| [143](../143.%20Reorder%20List/) 重排 | 三件套全用 | 先存再写 | 左中点切 → 反转后半 → 交替合并;前半 ≥ 后半所以只判 `second` |
| [148](../148.%20Sort%20List/) 排序 | 归并排序 | dummy + 尾插 + 先存再写 | 左中点(`fast = head.next`)切开 → 递归两半 → 21 的归并;n=2 必须切得开 |
| [203](../203.%20Remove%20Linked%20List%20Elements/) 删指定值 | 删除 | dummy + 删前驱 | 删了 prev 不动,没删 prev 才走 |
| [83](../83.%20Remove%20Duplicates%20from%20Sorted%20List/) 有序去重 | 删除 | 删前驱 | 只比相邻;头不会被删,单游标即可 |
| [2](../2.%20Add%20Two%20Numbers/) 两数相加 | 模拟 | dummy + 尾插 | 循环条件 `l1 or l2 or carry`,缺的一位当 0;`//` 取进位,`%` 取本位 |
| [138](../138.%20Copy%20List%20with%20Random%20Pointer/) 复制带随机指针 | 图克隆 | 哈希 | 两趟:先建 原→新 表,再查表连边;key 是节点不是 val |
| [146](../146.%20LRU%20Cache/) LRU | 双向链表 + 哈希 | 头尾哨兵 | unlink + push_front 两个原语;每次改动数指针 |
| [287](../287.%20Find%20the%20Duplicate%20Number/) 找重复数 | 隐式链表 | Floyd | `i → nums[i]`,重复值 = 环入口 |
| [707](../707.%20Design%20Linked%20List/) 设计链表 | 原语练习 | dummy + 删前驱 | 还没写;适合拿来把原语 1–3 各手写一遍 |

### 2 的简化写法

2 的三分支 `if l1 and l2 / elif l1 / elif l2` 可以压成一行,缺的那条当 0:

```python
v = carry + (l1.val if l1 else 0) + (l2.val if l2 else 0)
carry, digit = divmod(v, 10)
```

循环条件里带上 `carry`,最高位进位(`5 + 5 = 10`)就不用在循环外补节点。

---

### 速记

1. 头可能被删 / 被换 / 还不存在 → dummy,返回 `dummy.next`
2. 删节点要停在前驱;**删了 prev 不动**
3. 建新链 = dummy + tail 尾插;归并收尾 `tail.next = l1 or l2`
4. 写 `.next` 前先存;切开前先存右半的头
5. 判同一节点用 `is`,哈希表 key 用节点本身
6. 双向链表头尾都放哨兵;摘下改 2 根,插入改 4 根
7. 看到 `i → f(i)` 且出度为 1 → 隐式链表,判环 / 找入口套 Floyd
8. 三件套(中点 / 反转 / 交替合并)和自测脚手架见 [linked-list-template.md](../notes/linked-list-template.md)
