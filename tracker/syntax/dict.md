# Python dict 语法坑

读法和 [str.md](str.md) 一样：**从头通读**当 checklist（写哈希表 / 设计题之前扫一眼），
或者在看板里 `🧠 复习 → 语法` 按 FSRS 抽卡。格式约定见 [dashboard/syntax.py](../dashboard/syntax.py)。

收录标准同样是**只收自己真栽过的**。

---

## LRU 淘汰尾节点时，想把它的 key 从 map 里删掉，怎么写

```python
# 已经把 queue_tail 从双向链表上摘下来了
queue_tail.value = -1
# self.map[queue_tail.key] change it to inplace -1?
```

---

```python
del self.map[queue_tail.key]          # ✔ 按 key 删，O(1)
```

三种删法，区别在 key 不存在时：

| | key 不存在时 | 返回值 |
|---|---|---|
| `del d[k]` | `KeyError` | 无（是语句，不是表达式） |
| `d.pop(k)` | `KeyError` | 被删的 value |
| `d.pop(k, None)` | 不报错 | 被删的 value，没有就是 `None` |

`del` 后面跟的是**下标表达式** `d[k]`，不是 `d.del(k)` / `d.remove(k)`
（dict 没有 `remove`，那是 list 和 set 的）。

不会删就退而求其次"把 value 标成 -1 当墓碑"，是这道题真正栽的地方：

- **节点留在 map 里**：`key in self.map` 对已淘汰的 key 也是 True，
  `get` / `put` 里到处都得补一句 `value != -1` 的特判，漏一处就错；
- **`size` 也跟着忘了减**：墓碑让人觉得"已经删了"，`size` 只增不减 →
  后面更新已有 key 时也会触发淘汰，把不该淘汰的节点踢掉；
- map 只增不减，内存也一直涨。

真删掉（`del` + `self.size -= 1`）之后，那些特判全部可以删，`key in self.map` 重新等于"在缓存里"。

栽过：146

## 想按 value 从大到小遍历 dict 的 key，这样写对吗

```python
cnt = {"a": 1, "b": 4, "c": 2}
for ch in sorted(cnt, key=cnt.values, reverse=True):
    ...
```

---

```python
for ch in sorted(cnt, key=cnt.get, reverse=True):   # ✔ ['b', 'c', 'a']
```

拆开看：

- `sorted(cnt)` 遍历 dict 拿到的是 **key**，返回的也是 key 的 list
- `key=` 要的是**函数**：传进一个元素，返回按什么排。`sorted` 对每个 key 调一次 `cnt.get(ch)` 拿到个数，按个数排，但返回的还是 key
- 传的是 `cnt.get` **不带括号**，把函数本身交给 `sorted` 去调

`cnt.values` 错在：它不收参数，返回的是**全部** value，不是「这个 key 的 value」→ 一调就 `TypeError`。

等价写法：`key=lambda ch: cnt[ch]`。

同一个 `key=` 在 `max` / `min` / `list.sort` 里通用：`max(cnt, key=cnt.get)` 一行就是「个数最多的那个 key」，
不用手写 `if mx == cnt["a"] … elif …` 那一串。

栽过：1405
