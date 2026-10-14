---
title: heapq
status: draft
order: 4
related: [/structures/heap]
---

# heapq

## 一句话

**不是一个类，是一组作用在普通 `list` 上的函数**，把 list 当完全二叉树维护成**小根堆**。

## 底层长什么样

下标 `i` 的孩子是 `2i+1` 和 `2i+2`，父亲是 `(i-1)//2`。只保证「父 ≤ 子」，兄弟之间、不同子树之间没有顺序：

```
          1                 list: [1, 3, 2, 7, 4, 5]
        /   \                       0  1  2  3  4  5
       3     2
      / \   /
     7   4 5
```

`heappush` 放到末尾再往上浮，`heappop` 把末尾挪到根再往下沉，都只走一条根到叶的路径，O(log n)。

## 复杂度

| 操作 | 写法 | 复杂度 |
|---|---|---|
| 建堆 | `heapify(h)` | **O(n)**，原地 |
| 插入 | `heappush(h, x)` | O(log n) |
| 弹最小 | `heappop(h)` | O(log n) |
| 看最小 | `h[0]` | O(1) |
| 先推再弹 | `heappushpop(h, x)` | O(log n)，比分两步快 |
| 先弹再推 | `heapreplace(h, x)` | O(log n)，堆不能是空的 |
| 前 k 大 / 小 | `nlargest(k, it)` / `nsmallest` | O(n log k) |

## 由此而来的坑

- **只有小根堆**：大根堆存 `-x`，取出来再取负。Python 3.14 起有了 `heappush_max` 等函数，
  但 LeetCode 的环境不一定这么新，面试里默认还是取负。
- **`h[1]` 不是第二小**：第二小在 `h[1]` 和 `h[2]` 之间，没有保证。要第 k 小就弹 k 次。
- **元组比较打平**：`(dist, node)` 里 `dist` 相等时会去比 `node`，`node` 是 `ListNode` 这种不能比大小的东西就抛 `TypeError`。
  中间垫一个自增计数：`(dist, i, node)`（LC 23）。
- **以为 `heapify` 返回新堆**：它原地改、返回 `None`。`h = heapify(nums)` 之后 `h` 是 `None`。
- **改了元素没重建**：堆里的值被外面改了，堆性质就坏了。要么 `heapify` 重来，要么懒删除（弹出时再判断过期）。

## 什么时候用

- 前 k 大：维护**大小为 k 的小根堆**，比 k 小的直接扔 —— O(n log k)（LC 215、347、973）。
- 数据流中位数：一个大根堆放较小的一半，一个小根堆放较大的一半（LC 295）。
- 多路归并：堆里放每一路当前的头（LC 23）。
