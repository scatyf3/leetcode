---
title: 计数
status: draft
order: 14
alias: []
related: [/paradigms/hash, /paradigms/sliding-window, /structures/hash-table]
---

# 计数

很多题只关心**每种东西出现了几次**，不关心在哪、按什么顺序 —— 把输入看成一个多重集，答案只由那张计数表决定。
于是：比两个串 = 比两张表；窗口滑一格 = 表里一个 +1、一个 -1；问「最多的是谁 / 前 k 多」= 在表上再做一次选择。
拿什么装这张表（`Counter`、`[0] * 26`、下标当频次的桶）是值域问题，见 [hash-table.md](../structures/hash-table.md) §2。

## 1. 比两张表：242 / 49

242 不用数两遍再比对，让 t **消耗** s 数出来的库存，一张表就够：

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        count = defaultdict(int)      # 访问缺失 key 自动得 0, 省掉 if-else
        for a, b in zip(s, t):        # 长度已相等, 可以并排走
            count[a] += 1             # s 的字符: 入库
            count[b] -= 1             # t 的字符: 出库
        return all(v == 0 for v in count.values())
```

判「全为 0」不能写 `if count:`：抵消完键还在，只是值变成了 0。一行版是 `Counter(s) == Counter(t)`。

49 把这张表本身当成「同一组必然相同」的范式：26 位计数的 `tuple` 当 key（list 不可 hash），
比 `"".join(sorted(s))` 少一个 log。见 [hash-table.md](../structures/hash-table.md) §3 §5。

## 2. 窗口里的计数：567 / 438 / 76 / 424

计数能进滑窗，是因为它**可撤销**：进窗 +1、出窗 -1 互为逆操作。骨架见 [sliding-window.md](sliding-window.md)，
这里只看四题的计数表各自是什么语义：

| 题 | 窗口 | 计数表 | 合法 ⟺ |
|---|---|---|---|
| 567 | 定长 `len(s1)` | `win` 跟着滚，`need` 建好不动 | `win == need` |
| 438 | 定长 `len(p)` | `Counter(p)` 当 need：进窗 -、出窗 + | 全为 0 |
| 76 | 变长，求最短 | `Counter(t)` 当 need：进窗 -、出窗 + | 全部 ≤ 0（覆盖了 t） |
| 424 | 变长，求最长 | 窗口里每个字母几个 | 窗口长 − **最大频次** ≤ k |

567 定长，每步 `win[s2[r]] += 1; win[s2[r - n]] -= 1` 然后比一次，`l` 都不用存。
`win == need` 能直接比，是因为 Python 3.10+ 的 `Counter.__eq__` 忽略 0 计数（`Counter({'a': 0}) == Counter()`）。

踩过的坑都出在「表和窗口对不上」：

- **别在归零时 `del` 键、拿 `len(need) == 0` 判合法**（567）：`del` 不可逆，那个字符出窗时还不回来。
  `s1="abc", s2="abxc"` 假阳性。状态显式存成数，别用容器的 size 或键在不在来表达
- **减到 0 不删键**（424）：`len(cnt)` 会把值为 0 的键也数进去；`a - b` 会丢掉负数，要负数用 `a.subtract(b)`
- **`enumerate(cnt)` 拿到的是键不是值**（567）：要值 `cnt.values()`，要键值对 `cnt.items()`
- **只要最大频次，不要众数是谁**（424）：判定式里只出现 `max(cnt.values())`；字母表是常数，这一步不改变复杂度
- **`missing` 标量不一定更快**（76 / 567）：全量比较能降成维护一个「还差几个」的整数，但字母表只有 26 时，
  CPython 里 26 次 C 层比较实测反而更快，默认写全量比较

## 3. 频次当下标：347 / 621 / 287

- **347**：把 `元素 → 频次` 反过来建 `buckets[freq]`。频次一定落在 `[1, n]`，所以能开数组，下标白送了从高到低的顺序，
  O(n) 越过比较排序的下界。推导和实测在 [hash-table.md](../structures/hash-table.md) §2 §6。坑：一个桶可能只要其中几个，
  `len(res) == k` 要在内层就 return
- **621**：整张表只用得上两个数 —— 最大频次 `max_cnt` 和并列最多的有几种，见 [greedy.md](greedy.md) §2
- **287**：计数在**值域**上做：`C(v) = nums 里 ≤ v 的有几个`，`C(v) > v` 划出 `F…F T…T`，二分找第一个 T，
  见 [binary-search.md](binary-search.md)。坑：重复值可以出现多次、别的值缺席时 `C(v)` 可以 `< v`，`==` 和 `<` 走同一个分支

## 4. 压成 O(1)：169 Boyer-Moore

问题只是「谁出现超过一半」时，整张表可以压成一个 `(candidate, count)`：不同的元素两两抵消，众数比其他所有加起来还多，抵消完一定剩它。

```python
class Solution:
    def majorityElement(self, nums):
        count = 0
        candidate = None
        for num in nums:
            if count == 0:        # 前面的全抵消完了, 换候选
                candidate = num
            count += 1 if num == candidate else -1
        return candidate
```

代价是三条限制，424 想借它来维护最大频次时全撞上了：

1. 它给的是**谁**，不是**几个**；424 的判定式要的恰恰是次数
2. 必须保证众数 > n/2，不保证时结果是垃圾值
3. **不可逆**：抵消掉的信息已经丢了，`remove(arr[l])` 撤不回来，所以进不了滑窗
