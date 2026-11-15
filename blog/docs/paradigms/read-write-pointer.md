---
title: 读写指针
status: draft
order: 17
parent: two-pointer
alias: []
related: [/paradigms/two-pointer, /structures/array, /structures/hash-table]
---

# 读写指针

一个指针 `r` 老老实实读完每一格，另一个指针 `w` 只在「这个要留下」时才写一次、往前一格。
`r` 永远跑在 `w` 前面，所以 `w` 要踩的格子早就读过了，原地写不会丢数据 —— 整个套路就靠这一条。
三段不变式（kept / junk / unread）、覆盖式和交换式怎么选，写在 [array.md](../structures/array.md) §「读写指针」；
它在双指针里属于「同向·快慢」一族，见 [two-pointer.md](two-pointer.md) §2。这一页只讲怎么认出来、
以及 26 / 27 之外的两个变体（283 交换、75 三段）。

## SOP

坑全来自 26、27、75、443 的 sol 和 obs。

1. **先问每个元素的目的地由谁定。** 由顺序定是读写指针，由值定是 cyclic sort，见「怎么认出来」。
2. **只要前 k 个就覆盖，尾部也要对就交换。** 27 不管 `[w, n)` 里剩什么，283 要 0 真的待在尾部。
3. **定死 `w` 指什么。** 指下一个写入位就 `return w`（27）；指最后一个有效元素就 `return k + 1`（26）。
4. **用 `while`，只在该推进时推进。** 换过来的数还没读，读指针就不能动（75 一趟版、27 首尾交换版）。

第 N 步栽过的坑：

- 第 2 步 —— **26** wa1：用 set 去重、把重复的换到尾部，既没用上「已排序」，又打乱了前 k 个的顺序。
- 第 3 步 —— **26** sol2 在返回值上写了「indexing issue again」。**443**：`w` 一次写好几格，`+1` 容易多算，见「26 / 27」一节末尾。
- 第 4 步 —— **75**：sol.py 交换后 `read` 没动，`w` 跑到 `r` 前面，最后越界。

## 怎么认出来

题面三件套：**原地**、**O(1) 额外空间**、**返回「前 k 个」或长度 / 保持相对顺序**。
再问一句：**每个元素去哪，是由什么决定的？**

| 目的地由谁定 | 套路 | 题 |
|---|---|---|
| **顺序**：留下的依次排到 `w`，只看「留不留」 | 读写指针 | 26、27、283、75、443 |
| **值本身**：v 的家是 v-1 | 原地哈希（cyclic sort） | 41、448 |

后一种长得像读写指针（也是原地、也在交换），但只有一个指针在动、元素会被往前送回去。
两者的逐项对比见 [hash-table.md](../structures/hash-table.md) §8「长得像读写指针，但不是」。

## 26 / 27：覆盖式模板

27 是模板原型：`for r` 扫一遍，`if nums[r] != val: nums[w] = nums[r]; w += 1`，最后 `return w` ——
`w` 指**下一个要写的位置**（一条缝），同时就是已保留的个数，不用另开计数变量（27 sol1 多开了一个 `no_eq_count`）。
26 的「留不留」要回看**最后一个已保留的值**，这时让 `k` 指最后一个有效元素更顺（约定 B），代价是返回 `k + 1`
—— 26 sol2 就在这里写了「indexing issue again」。两种约定、初值和返回值怎么推，见
[notes/two-pointer-array-partition.md](https://github.com/scatyf3/leetcode/blob/main/tracker/notes/two-pointer-array-partition.md)。
26 的 wa1 是反面：用 set 去重、把重复的换到尾部，既没用上「已排序」，又打乱了前 k 个的顺序。

[443 String Compression](https://github.com/scatyf3/leetcode/blob/main/tracker/443.%20String%20Compression/sol.py) 也是覆盖式，只是 `w` 一次要写好几格：字符一格，计数的每一位各一格。
sol.py 里 `len_nums` 从 1 起算，已经含了字符那一格，所以是 `valid_idx += len_nums`，不是 `1 + len_nums`（注释里特意记了）。
原地写也踩不到未读数据：一组 k 个（k ≥ 2）压成 `1 + 位数` 格，不超过 k，`w` 追不上 `r`。
sol.py 先把整串读进 `char_list` / `res` 两个 list 再回写，额外空间 O(n)；有这条保证，其实可以边读边写。

## 283 Move Zeroes：交换，不是覆盖

27 不管 `[w, n)` 里剩什么，283 要求 0 真的出现在尾部。把覆盖换成交换：`[w, r)` 里全是 0，
换到 `w` 的必是一个 0（或 `w == r` 自己换自己），非零按原顺序压到前面。

```python
r = 0
w = 0
while r != len(nums):
    if nums[r] != 0:
        tmp = nums[w]
        nums[w] = nums[r]
        nums[r] = tmp       # 换过来的一定是 0, 或者 w == r
        w += 1
    r += 1
```

## 75 Sort Colors：两段变三段

**分趟做 283**：第一趟把 0 换到 `w` 前面，第二趟从 `w` 接着把 1 换上来，2 自然留在尾部（第三趟多余）。
sol.py 交换后 `read` 没动：`w == r` 自己换自己之后 `w` 跑到 `r` 前面，下一轮把归好位的 0 又换走，最后越界。

```python
def sortColors(nums):
    w = 0
    for color in (0, 1):            # 每一趟都是一遍 283
        r = w
        while r < len(nums):
            if nums[r] == color:
                nums[w], nums[r] = nums[r], nums[w]
                w += 1
            r += 1                  # 换没换都要 +1
```

Follow-up 要一趟：读指针 `i` 两边各开一个写入区，0 往左边 `lo` 写，2 往右边 `hi` 写：

```
    0        lo         i          hi        n
    [-- 0 --|--- 1 ---|-- unread --|--- 2 ---]
```

```python
def sortColors_one_pass(nums):
    lo, i, hi = 0, 0, len(nums) - 1
    while i <= hi:                  # [i, hi] 是未读区, 闭区间
        if nums[i] == 0:
            nums[lo], nums[i] = nums[i], nums[lo]
            lo += 1
            i += 1                  # 从 lo 换来的是 1 (或 lo == i 自己换自己), 都读过了
        elif nums[i] == 2:
            nums[i], nums[hi] = nums[hi], nums[i]
            hi -= 1                 # 从 hi 换来的还没读, i 不动
        else:
            i += 1
```

和右端换完 `i` **不能前进** —— 27 的首尾交换版（sol1）踩过同一条：换过来的数还没检查，
所以 obs1 的结论是「用 `while` 不用 `for`，只在没交换时推进下标」；未读区是闭区间，条件是 `i <= hi`。
