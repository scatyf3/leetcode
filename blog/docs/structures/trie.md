---
title: 字典树（Trie）
status: draft
order: 13
alias: []
related: [/structures/string, /structures/tree, /structures/hash-table]
---

# 字典树（Trie）

## 一句话

**把一堆字符串的公共前缀合并成一棵树**：每条边是一个字符，每个节点代表「从根走到这里拼出来的那个前缀」。
它多维护的信息是**前缀关系** —— 哈希表只能回答「这个串在不在」，Trie 还能回答「有多少串以它开头」。

## 长什么样

插入 `app`、`apple`、`bat` 之后：

```
        (root)              root 是空的哨兵，不代表任何字符
        /    \
       a      b
       |      |
       p      a
       |      |
       p*     t*            * = is_end：有单词恰好在这里结束
       |
       l
       |
       e*
```

- `app` 和 `apple` 共用 `a → p → p` 这条路，公共前缀只存一份。
- **节点上必须有 `is_end`**。只插了 `apple` 时，`a → p → p` 这条路也存在，
  没有这个标记就分不清 `app` 是「插过的单词」还是「只是某个单词的前缀」 —— 这正是 `search` 和 `startsWith` 的区别。

## 模板（LC 208）

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # char -> TrieNode，一个字符一条边
        self.is_end = False     # 有没有单词恰好在这里结束

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()   # 没有这条边就新建
            node = node.children[c]
        node.is_end = True

    def _walk(self, s):
        """沿着 s 往下走：走通了返回最后一个节点，中途断了返回 None"""
        node = self.root
        for c in s:
            if c not in node.children:
                return None
            node = node.children[c]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix):
        return self._walk(prefix) is not None
```

`search` 和 `startsWith` 只差最后一步看不看 `is_end`，所以抽一个 `_walk` 共用。
插入和查找都**直接迭代**，不用递归：每一步只往一个孩子走，没有分叉，用不上递归的回溯能力。

## 复杂度：赢在前缀，不赢在查找

| 操作 | Trie | 字符串的 `set` |
|---|---|---|
| 插入 / 精确查找长度 L 的串 | O(L) | O(L)（算 hash 要读完整个串） |
| 「有没有串以 p 开头」 | O(len p) | O(总长度)，只能逐个比 |
| 「以 p 开头的有几个」 | 节点上加计数，O(len p) | 同上 |
| 空间 | 每个字符一个节点，公共前缀共享 | 每个串完整存一份 |

精确查找两者一样快 —— 别以为 Trie 比哈希表快。**题目问到「前缀」时才轮到 Trie。**

`children` 用 `dict` 还是长度 26 的数组：和 [hash-table.md](hash-table.md) §2 是同一个判断。
字符集小且固定（只有小写字母）就能开数组，常数更小；但每个节点都要占 26 格，节点多的时候很费内存。
不确定就用 `dict`。

## 节点上存计数：`end` 和 `pass`

把 `is_end` 换成两个计数，Trie 就能回答「有几个」：

| 字段 | 含义 | 用来回答 |
|---|---|---|
| `end` | 有几个串**恰好在这里结束** | 「这个串出现过几次」 |
| `pass` | 有几个串**经过这里**（含在这里结束的） | 「以这个前缀开头的串有几个」 |

### 例：数后缀对

给一组字符串，数有多少对 `(i, j)`（`i < j`）满足：两串相等，或者一个是另一个的后缀。

暴力是两两比较，O(n² · L)。用 Trie 可以做到 O(总长度)，要过两道弯：

1. **后缀问题先反转成前缀问题**。`s` 是 `t` 的后缀，等价于 `reverse(s)` 是 `reverse(t)` 的前缀。
   所以每个串都**反着**插进 Trie。（LC 820 Short Encoding of Words 也是这一招。）
2. **边插边数**。插第 j 个串之前，Trie 里正好是它前面那些串，沿着它的路径走一遍就能数出它和前面的串能配几对：
   - 途经的节点（不含终点）上的 `end`：前面有几个串在这里结束了，它们是我的**真后缀**。
   - 终点上的 `pass`：前面有几个串经过我的终点，我是**它们的**后缀。相等的串也走到同一个终点，所以已经算在这里面了。
     **不要再加终点的 `end`**，否则相等的串会被数两次。

```python
class Node:
    def __init__(self):
        self.ch = {}
        self.end = 0
        self.pass_ = 0

def count_suffix_pairs(words):
    root, ans = Node(), 0
    for w in words:
        node, rw = root, w[::-1]                      # 后缀 → 反转成前缀
        for i, c in enumerate(rw):
            node = node.ch.setdefault(c, Node())
            if i < len(rw) - 1:
                ans += node.end                       # 途经：之前的串是我的真后缀
            else:
                ans += node.pass_                     # 终点：我是之前的串的后缀（含相等）
            node.pass_ += 1
        node.end += 1
    return ans
```

这一题的关键是「先查后插」，和 [hash-table.md](hash-table.md) §4 的 2Sum 一样：
先数完再把自己插进去，才不会自己和自己配对。
同族的题：LC 3045 Count Prefix and Suffix Pairs II（要求同时是前缀和后缀，把每个串拆成 `(s[i], s[-1-i])` 的字符对再插）。

## 什么时候想到 Trie

| 信号 | 做法 | 题 |
|---|---|---|
| 「以……开头」「前缀」 | 标准 Trie | LC 208 |
| 带通配符 `.` 的查找 | 碰到 `.` 就在 Trie 上 DFS 所有孩子 | LC 211 |
| 在网格里同时找一堆单词 | 单词建 Trie，网格回溯时沿 Trie 走，走不通就剪枝 | LC 212（[回溯](../paradigms/backtracking.md) × Trie） |
| 「后缀」「以……结尾」 | **反转后**插 Trie | LC 820、上面的后缀对 |
| 数「有几个串满足某种前缀 / 后缀关系」 | 节点上存 `end` / `pass` 计数，边插边数 | LC 3045 |

## 由此而来的坑

- **忘了 `is_end`**，`search` 就退化成了 `startsWith`。
- **计数题里分清 `end` 和 `pass`**：一个是「在这结束」，一个是「从这经过」。
  后缀对那题里，终点上加错一个，相等的串就会被重复计数。
- **用标准 Trie，不用压缩 Trie**。压缩 Trie（一个节点存一段字符串）省空间，但插入时要切分节点，面试里没必要（208 的 note）。
