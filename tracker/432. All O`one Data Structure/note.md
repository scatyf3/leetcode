# 432. All O`one Data Structure

想了个双hash的思路，但没有利用「counter」一次只能inc1 的feature
```
        # string => counter's hash table?
        # Note that each function must run in O(1) average time complexity
        # hash + double ended linkedlist(lru
        # counter => list of string，这样inc和dec的时候需要在hash里查找
        # string => (counter, list index)
        # 但好像「counter => list of string」，这里remove并非O(1)，改成双向链表就是答案了吗
        self.string_counter = {}
        self.string_fast_search = {}
```

---

### 难点不在计数，在 O(1) 拿最大 / 最小

`key → 次数` 一张表，inc / dec 就 O(1) 了；难的是**次数一直在变，还要 O(1) 拿 max / min**。
堆不行：inc / dec 要调整位置，O(log n)。

能做到 O(1) 靠的就是上面说的没用上的 feature：**次数一次只变 1** → key 只会挪到**相邻**的桶。
「次数 → key 集合」里集合用 `set`（增删平均 O(1)），不用 list，也不用在桶里再套链表。

### 两个版本

| | [sol.py](sol.py)：两张哈希表 + `mn` / `mx` | [sol_dll.py](sol_dll.py)：桶串成双向链表 |
|---|---|---|
| 结构 | `cnt: key → 次数`，`bucket: 次数 → set`，两个变量记最小 / 最大次数 | 每个桶 `(次数, set)` 按次数串成双链表 + `where: key → 桶` |
| key 换桶 | O(1) | O(1) |
| 桶空了找邻居 | 隔壁桶一定存在（key 刚搬过去），O(1) | O(1) |
| **dec 到 0 且次数 1 的桶空了** | 往上扫找下一个非空次数，**O(最大次数)** | `head.next`，O(1) |
| 代码量 | 少，没有指针 | 多两个原语 `_insert_after` / `_remove` |

反例（为什么 sol.py 不是严格 O(1)）：`inc a` × 1000，然后 `inc b`、`dec b` 交替 —— 每次 `dec b` 都从 2 扫到 1000。
题目最多 5×10⁴ 次调用，LeetCode 上大概率能过；面试被问「每个操作都 O(1) 吗」要主动说这个例外，
再说「严格 O(1) 就把桶用双链表串起来」。

> **链表在这里提供的就是一件事：「下一个非空的次数」不用找，`cur.next` 直接给。**

### 双链表版的几个设计

- **新 key 当作在 head 里**：`where.get(key, self.head)`，head 次数是 0，新 key 和「次数 +1」走同一条路
- **先放进新桶，再从旧桶删**：反过来的话旧桶可能先被摘掉，新桶就没法相对它定位
- **哨兵次数 0 和 inf**：`nxt.cnt != cur.cnt + 1` 碰到 tail 自然成立，不用特判
- **head 不能删**：inc 里 `cur is not self.head` 才去旧桶删
- 和 [146 LRU](../146.%20LRU%20Cache/note.md) 同一个骨架：哈希表 O(1) 定位 + 双链表 O(1) 维护顺序 + 指针只在两个原语里写。
  区别是 LRU 的节点是一个 key、按使用时间排；432 的节点是一桶 key、按次数排

### 小坑

- `set` 增删是**平均** O(1)（哈希冲突最坏 O(n)），题目要求的也是 average
- `next(iter(s))` 取一个元素：set 删元素后不缩容，删得很空时要跳过空槽。这题桶一空就整个扔掉，影响可以忽略

自测：inc a, b, b, c, c, c → max c / min a；dec c ×3 → max b / min a；dec a → max b / min b；dec b ×2 → 都是 `""`。

两个版本都和暴力解随机对拍过（3000 组操作序列）。
