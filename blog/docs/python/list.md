---
title: list
status: draft
order: 1
related: [/structures/array, /structures/stack-queue]
---

# list

## 一句话

**存指针的动态数组**。尾部操作均摊 O(1)，其余位置的插删都要挪后面的元素，O(n)。

## 底层长什么样

一块连续内存，每格是一个指向 Python 对象的指针（不是值本身）。容量不够时重新申请一块更大的再整体拷过去，
每次多分大约 1/8 的余量，所以 `append` 偶尔一次 O(n)，摊下来 O(1)。

```
ob_item → [ *0 | *1 | *2 | *3 |  空  |  空  ]
            len = 4           allocated = 6
```

## 复杂度

| 操作 | 复杂度 | 为什么 |
|---|---|---|
| `a[i]` / `a[i] = x` | O(1) | 连续内存，算地址 |
| `append(x)` / `pop()` | O(1) 均摊 | 只碰尾巴 |
| `insert(0, x)` / `pop(0)` | **O(n)** | 后面全部往后 / 往前挪一格 |
| `x in a` / `a.index(x)` / `a.remove(x)` | O(n) | 线性扫 |
| `a[l:r]` | O(r − l) | 切片是**拷贝** |
| `a.sort()` / `sorted(a)` | O(n log n) | Timsort，稳定 |
| `len(a)` | O(1) | 存着的 |

## 由此而来的坑

- **拿 list 当队列**：`pop(0)` 是 O(n)，BFS 里每层都这么弹就成了 O(n²)。队列用 [deque](deque.md)。
- **`[[0] * n] * m`**：外层乘的是**指针**，m 行全指向同一个内层 list，改一行全改。写 `[[0] * n for _ in range(m)]`。
- **切片当 O(1) 用**：递归里传 `nums[1:]` 每层都拷一份，总共 O(n²)。传下标。
- **边遍历边删**：`for x in a: a.remove(x)` 会跳元素。倒着按下标删，或者建新 list。

## 当栈用

`append` 进、`pop()` 出、`a[-1]` 看栈顶，全是 O(1)。空栈 `a[-1]` 会抛 `IndexError`，先判 `if a`。
