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

通用原理（桶、碰撞、负载因子、扩容）见 [structures/hash-table.md](../structures/hash-table.md) §0，这里只讲 CPython 的具体做法。

### dict：两张表

CPython 3.6 起的 `dict` 是「紧凑」布局：

```
indices  稀疏，长度是 2 的幂（最少 8）。每格存一个 entries 的下标，或者「空」/「墓碑」
entries  稠密，按插入顺序追加 (hash, key, value)
```

为什么拆两张：真正占地方的 `(hash, key, value)` 只在 `entries` 里按需追加，空出来的格子只在
`indices` 里浪费一个小整数（表小的时候只占 1 字节）。而且 `entries` 是按插入顺序追加的，
所以**遍历顺序 = 插入顺序**，3.7 起这是语言保证。

### 走一遍：`d[3] = 'a'; d[11] = 'b'; d[6] = 'c'`

小整数的 hash 就是它自己，`indices` 长度 8，所以 `mask = 7`，起始格是 `hash & 7`（等价于 `% 8`）：

```
d[3]  = 'a'   3 & 7 = 3   indices[3] 空 → entries 追加到 0 号，indices[3] = 0
d[11] = 'b'  11 & 7 = 3   indices[3] 被占 → 按探测序列找下一格（见下）→ 0 号格空
                          → entries 追加到 1 号，indices[0] = 1
d[6]  = 'c'   6 & 7 = 6   indices[6] 空 → entries 追加到 2 号，indices[6] = 2

indices: [ 1, -, -, 0, -, -, 2, - ]
entries: [ (3, 3, 'a'), (11, 11, 'b'), (6, 6, 'c') ]
```

查 `d[11]` 就是把这条路再走一遍：先看 `indices[3]`，指向 entries[0]，key 是 3，`3 != 11`，继续探测；
下一格是 `indices[0]`，指向 entries[1]，key 是 11，命中，返回 `'b'`。
比较时先看是不是同一个对象（`is`），再看 hash 是否相等，最后才调 `==`，便宜的检查放在前面。

### 探测序列：不是逐格往后

被占了以后不是试 `i + 1`，而是：

```python
perturb = hash
i = hash & mask
while 这一格被占且不是要找的 key:
    perturb >>= 5
    i = (5 * i + perturb + 1) & mask
```

- `5 * i + 1` 这个递推在 2 的幂长度的表上会把每一格都走到一遍，所以只要表没满，一定能找到空格。
- `perturb` 把 hash 的高位逐步掺进来。只看 `hash & mask` 等于只用了 hash 的低几位，
  低位相同的 key 会一直撞在一起，掺进高位就能把它们分开。上例里 11 的 `perturb` 右移 5 位后已经是 0，
  所以下一格就是 `(5*3 + 0 + 1) & 7 = 0`。

### 删除与扩容

- **删除**：`indices` 那一格改成墓碑，`entries` 那一条清空，但不挪动别的条目。原因见 hash-table.md §0：
  直接清空会截断别人的探测序列。
- **扩容**：`entries` 用满（大约是 `indices` 长度的 2/3）就换一张更大的表，把还活着的条目重新插一遍。
  墓碑和空洞在这一步一起被清理掉。

### set：另一套实现

`set` 的源码和 `dict` 是两套。它的每一格直接存 `(key, hash)`，没有 `entries` 那一层，所以**没有顺序**可言。
碰撞时先线性试几个相邻格（对 cache 友好），再按扰动跳走。它扩容得也比 `dict` 早，大约 60% 满就扩。

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
