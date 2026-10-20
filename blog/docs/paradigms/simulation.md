---
title: 模拟
status: draft
order: 16
alias: []
related: [/structures/matrix, /structures/linked-list, /structures/heap, /paradigms/state-machine]
---

# 模拟

模拟题没有要发明的算法：题面已经把过程讲清楚了（逐位相加、一圈圈走、一对对换），照着做一遍就是答案，
复杂度就是过程本身的长度。难度全在**记账** —— 每一步要更新哪几个变量、循环什么时候停、边界上会不会多走或少走一格。
所以这一页不讲套路，只讲记账时的几条习惯，以及每道题具体的账记在哪。

## 认出来：没有候选可丢，也没有子问题可复用

双指针靠「丢掉不可能更优的候选」省时间，DP 靠「子问题的答案复用」。模拟两样都没有，
每一步都得真的做。直接做太慢的时候，答案通常不是换算法，而是**换一个让这一步变快的结构**：
1046 每轮都要「拿出最重的两块」，用 list 每轮找最大是 O(n)，换成堆就是 O(log n)，过程本身一点没变。

## 四条记账习惯

**1. 能用控制流表达的状态，就别提成变量。** 54 螺旋矩阵 pass1 想设一个 step 变量记「现在往哪走」，
然后卡在「我怎么知道我在哪个 step 里」—— 这个问题本身就说明设计错了。四个顺序排列的 `for`，
「在哪个循环里」就是那个状态。四边界法和两条守卫见 [matrix.md](../structures/matrix.md) §1。

**2. 先记录，再修改，两趟分开。** 73 矩阵置零边扫边置零，新写进去的 0 会被后面当成原有的 0，连锁清掉整张表。
第一趟只把零行、零列存进两个 set，第二趟再改。O(1) 空间版（借第一行 / 第一列当标记）见 [matrix.md](../structures/matrix.md) §4。

**3. 循环条件里带上所有「还没处理完」的东西。** 2 两数相加的条件是 `l1 or l2 or jw`：
漏了进位 `jw`，`5 + 5` 最高位的 1 就丢了。`%` 取当前位、`//` 取进位，别弄反。
压成一行 `divmod` 的写法见 [linked-list.md](../structures/linked-list.md) §「2 的简化写法」。

**4. 链表上的模拟：先画「改之前 / 改之后」，再逐根写指针。** 24 两两交换就是把
`prev → cur → nxt → nxt_nxt` 改成 `prev → nxt → cur → nxt_nxt`，三行赋值照着图写。
坑在换完之后：`cur` 成了这一对的尾巴，所以下一轮是 `prev = cur`，不是 `prev = nxt`。

## 25 Reverse Nodes in k-Group

24 是它 `k = 2` 的特例。自己那版先用两个数组存每组的 start / end，反转完再统一连线，非常容易连出环。
改成一组一组处理，每组只记三个节点：上一组的尾巴 `group_prev`、这一组的最后一个 `kth`、下一组的头 `group_next`。

```python
def reverseKGroup(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy                  # 上一组的尾巴
    while True:
        # 1. 走 k 步找这一组的最后一个节点; 不够 k 个就结束
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next           # 先存: 反转时 kth.next 会被改掉

        # 2. 反转这一组; prev 初值 = 反转后尾巴该指向的节点
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt

        # 3. 接回前面: 上一组尾巴 → 新头 kth; 旧头成了新尾巴
        old_head = group_prev.next
        group_prev.next = kth
        group_prev = old_head
```

关键是第 2 步 `prev` 的初值：设成 `group_next` 而不是 `None`，反转完尾巴就已经接上下一组，不用再连。
反转和「先存再写」本身见 [linked-list.md](../structures/linked-list.md) 原语 3。

## 其余几道的账

| 题 | 每一步记什么 | 坑 |
|---|---|---|
| 118 杨辉三角 | `prev = res[-1]`，新行首尾是 1，中间 `prev[j-1] + prev[j]` | 用 `l, r = 0, 1` 一对相邻下标滑到 `r < i`，边界拿不准就 print 一下 |
| 1046 最后一块石头 | 取反用 heapq 当最大堆，每轮弹两块，不等就压回差值 | 两个都是负数，差值写 `stone_1 - stone_2`（先弹出的更重）才保持负号；空堆返回 0 |
