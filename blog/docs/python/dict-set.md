---
title: dict / set
status: draft
order: 2
related: [/structures/hash-table]
---

# dict / set

## 一句话

**开放寻址的哈希表**。按 key 查、插、删均摊 O(1)；key 必须可哈希；`dict` 记住插入顺序，`set` 不记。

## 底层长什么样

CPython 3.6 起的 `dict` 是「紧凑」布局，两张表：

```
indices: [ -, 1, -, 0, -, 2, -, - ]      稀疏，存下标，哈希值决定落在哪格
entries: [ (h,k,v), (h,k,v), (h,k,v) ]   稠密，按插入顺序追加
```

哈希冲突时按一个扰动序列探测下一格（开放寻址，不是拉链）。
`indices` 用到大约 2/3 就扩容重建。删除只打个墓碑标记，不挪别人。

因为 `entries` 是按插入顺序追加的，**遍历顺序 = 插入顺序**（3.7 起是语言保证）。
`set` 是另一套实现，没有 `entries` 这层，所以**没有顺序**可言。

## 复杂度

| 操作 | 均摊 | 最坏 |
|---|---|---|
| `d[k]` / `d[k] = v` / `del d[k]` / `k in d` | O(1) | O(n)（全冲突） |
| `s.add(x)` / `x in s` / `s.discard(x)` | O(1) | O(n) |
| 遍历 | O(n) | |
| `s & t` | O(min(len s, len t)) | |
| `s \| t` | O(len s + len t) | |

## 由此而来的坑

- **list 不能当 key**：可变 → 不可哈希。转成 `tuple(lst)`；字母异位词分组常用 `tuple(sorted(s))` 或 26 位计数元组。
- **`d[k]` 不存在会抛 `KeyError`**：计数用 `d.get(k, 0) + 1`、`defaultdict(int)` 或 `Counter`。
- **`defaultdict` 一读就插**：`if d[k]:` 这种「只是看看」也会把 `k` 塞进去，之后遍历 / `len` 都变了。只读用 `k in d` 或 `d.get(k)`。
- **遍历时改大小**：`for k in d: del d[k]` 直接 `RuntimeError`。遍历 `list(d)`。
- **以为 set 有序**：小整数的 `set` 打印出来常常「看着」有序，那是哈希值恰好等于自己，不是保证。

## 常用的三个变体

| | 用在 |
|---|---|
| `collections.Counter` | 计数；`c.most_common(k)`；两个 Counter 能直接 `==` 比（滑窗异位词） |
| `collections.defaultdict(list)` | 分组：`g[key].append(x)` |
| `collections.OrderedDict` | 要 `move_to_end` / `popitem(last=False)` 的时候 —— 手写 LRU 的偷懒版 |

语法卡：[tracker/syntax/dict.md](https://github.com/scatyf3/leetcode/blob/main/tracker/syntax/dict.md)
