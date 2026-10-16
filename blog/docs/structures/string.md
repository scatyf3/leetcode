---
title: 字符串
status: draft
order: 7
alias: []
related: [/python/str, /structures/array, /structures/hash-table, /structures/trie]
---

# 字符串

字符串就是一个**不可变的字符数组**，数组上的技巧（滑窗、双指针、DP）几乎原样照搬。
它比普通数组多出来的只有两样：**字符集很小**（多数题只有 26 个小写字母，所以计数用 26 个桶就够），
以及题面里成对出现的**子串 / 子序列**两套问题，一个词就决定了解法族。
这一页是张地图：字符串自己的东西写在这里，套路去各自的页面。

## Python 里的字符串

底层和复杂度见 [python/str.md](../python/str.md)，这里只记做题时真撞上的：

- **不能原地改**：没有 `s[i] = 'x'`，也没有 `s.sort()`。要改就 `list(s)`，改完 `''.join`；
  要排序就 `''.join(sorted(s))`（49 第一反应写了 `s.sort()`）
- **攒结果用 list，最后 join**：回溯里 `cur` 是字符 list，结算时 `''.join(cur)`；
  写成 `str(cur)` 得到的是 `"['a', 'd']"`（17）
- **判字母数字用 `isalnum()`**：`isalpha()` 会漏数字，`"0P"` 判成回文（125）
- **数字当字符串处理**：`list(str(n))` 拆位，`int(''.join(digits))` 拼回；Python 没有 INT_MAX，自己写 `2**31 - 1`（556）

## 字符集有限：26 个桶

字符就是一个小整数，值域有界又连续，所以哈希表可以直接退化成长度 26 的数组
（判据见 [hash-table.md](hash-table.md) §2）。实际写的时候，`Counter` 和 `[0] * 26` 怎么选：

| 写法 | 什么时候 | 题 |
|---|---|---|
| `Counter` / `defaultdict(int)` | 默认。可读，两个 `Counter` 能直接 `==` | 242、438、567、76 |
| `[0] * 26` + `ord(c) - ord('a')` | 要当 dict 的 key（转 `tuple`），或真卡常数 | 49 |
| 一张表 `+1 / -1` 抵消 | 两串比字符组成：s 入库、t 出库，最后全 0 | 242 |

567 实测过：`list(26)` 比 `Counter` 快 4.5～14 倍，但最坏也就 20 ms，结论还是默认写 `Counter`。

计数表上踩过的坑：

- **`enumerate(dict)` 拿到的是键**，不是键值对；要值用 `.values()`，要键值对用 `.items()`（567）
- **计数归零时别 `del` 键**：滑窗的「进」和「出」必须是一对逆操作，删了键再配上 `in` 守卫，字符移出窗口时就还不回来（567）
- **减到 0 的键还在**：`len(cnt)` 不等于窗口里的字符种数，判「全部为 0」要看 `.values()`（424、242）

## 题型地图

拿到字符串题先看问的是哪种「子」：子串（substring）连续，子序列（subsequence）可以跳着取。
看错这一个词，后面全白搭 —— 对照表见 [notes/subseq-vs-substr.md](https://github.com/scatyf3/leetcode/blob/main/tracker/notes/subseq-vs-substr.md)。

| 问的是 | 套路 | 题 | 去哪看 |
|---|---|---|---|
| 连续子串的最长 / 最短 / 恰好是某个排列 | 滑动窗口（定长或变长） | 3、424、76、438、567 | [sliding-window.md](../paradigms/sliding-window.md) |
| 整串是不是回文 | 相向双指针，跳过非字母数字 | 125 | [two-pointer.md](../paradigms/two-pointer.md) |
| 回文子串（最长 / 计数） | 中心扩展（下一节） | 5、647 | [notes/palindrome-family.md](https://github.com/scatyf3/leetcode/blob/main/tracker/notes/palindrome-family.md) |
| 两个串比较 / 匹配 / 编辑 | 二维 DP，`dp[i][j]` = 两个前缀 | 1143、72 | [2d-dp.md](../paradigms/2d-dp.md) |
| 能不能切成词典里的词 | 一维 DP，下标是缝 | 139 | [1d-dp.md](../paradigms/1d-dp.md) |
| 括号、嵌套 | 栈 | 20、32、394 | [stack.md](../paradigms/stack.md) |
| 生成所有串 / 所有切法 | 回溯 | 17、22、131 | [backtracking.md](../paradigms/backtracking.md) |
| 一组串的公共前缀 | 字典树 | 208 | [trie.md](trie.md) |
| 按组成分组 | 范式键（排序串或计数元组） | 49 | [hash-table.md](hash-table.md) §5 |
| 每个字母的首末位置 | 区间合并 | 763 | [intervals.md](../paradigms/intervals.md) |
| 数字的「下一个排列」 | 字典序贪心 | 556 | [lexicographic-greedy.md](../paradigms/lexicographic-greedy.md) |
| 构造满足约束的最长串 | 贪心，每步取剩得最多的 | 1405 | [greedy.md](../paradigms/greedy.md) |

## 回文：枚举中心，不是枚举端点

回文是数组上没有的东西，单独说一句。它**不能滑窗**：`"aba"` 是回文，子串 `"ab"` 不是，
合法性不向下封闭，左边界不单调。但它满足另一种封闭：左右各缩一格还是回文 —— 所以从中心往外扩，扩不动就停。
5 的 `expand`：

```python
def expand(l: int, r: int) -> str:
    # 从中心 [l, r] 向两边扩, 返回能扩到的最长回文子串
    while l >= 0 and r < n and s[l] == s[r]:
        l -= 1
        r += 1
    # 退出时 l / r 已经站在第一个不合法的位置上; 切片右端是开区间, 正好省掉一个 -1
    return s[l + 1 : r]
```

奇中心传 `(i, i)`，偶中心传 `(i, i + 1)`，一共 `2n - 1` 个中心，**漏掉偶中心是最常见的 WA**。
偶中心不用先判 `s[i] == s[i+1]`，失配时 while 首轮就退出、返回 `""`。
647 是同一份骨架，把「留最长」换成「每扩成功一次 `cnt += 1`」。初稿的 5 个 bug、为什么「和反转串求最长公共子串」是错的，
见 [5 的 note](https://github.com/scatyf3/leetcode/blob/main/tracker/5.%20Longest%20Palindromic%20Substring/note.md)。

## 序列化：把别的结构压成一个字符串

字符串能当 dict 的 key、能用 `in` 找子串，所以有时先把别的结构**编码成字符串**，问题就换成了字符串问题。
编码要做到两点：**能还原**，以及**相邻的两段不会串味**。

**572 Subtree of Another Tree**：先序序列化，「子树」变成「子串」：

```python
def ser(node):
    if node is None:
        return "^#"
    return "^" + str(node.val) + ser(node.left) + ser(node.right)

return ser(subRoot) in ser(root)
```

两个分隔细节少一个就错：`#` 给空节点占位，否则 `[1,2]`（2 是左孩子）和 `[1,null,2]` 串成一样；
`^` 放在每个值前面，否则 `root=[12]`、`subRoot=[2]` 会因为 `"2"` 是 `"12"` 的子串误判。

**271 Encode and Decode Strings**（还没写）：一组任意字符串压成一个串再拆回来。
572 能用分隔符，是因为值都是整数、里面不会出现 `^`；271 的内容是任意字符，任何分隔符都可能出现在串里。
办法是**长度前缀**：每段写成 `长度 + '#' + 内容`，解码时先读到 `#` 拿到长度，再整段切走，内容里有没有 `#` 都无所谓。

```python
def encode(strs: list[str]) -> str:
    parts = []
    for s in strs:
        parts.append(str(len(s)) + "#" + s)
    return "".join(parts)

def decode(data: str) -> list[str]:
    res = []
    i = 0
    while i < len(data):
        j = data.index("#", i)          # 长度在 data[i:j]
        length = int(data[i:j])
        res.append(data[j + 1 : j + 1 + length])
        i = j + 1 + length              # 跳过整段内容, 不看里面有什么
    return res
```

树的序列化 / 反序列化（297）见 [dfs.md](../paradigms/dfs.md) §4。
