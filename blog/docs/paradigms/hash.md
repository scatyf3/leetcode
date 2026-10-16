---
title: 哈希
status: draft
order: 13
alias: []
related: [/structures/hash-table, /paradigms/counting, /paradigms/sliding-window]
---

# 哈希

和 [哈希表](../structures/hash-table.md) 的分工：那边讲结构本身（存什么、dict 还是桶、顺序、原地哈希），
这里只讲一个套路：**扫到 j 的时候，要在前面找一个 i 跟它配对 —— 那就把每个 i 的「配对特征」先存进表，
j 来了 O(1) 回查。** 暴力是双重循环，哈希把内层那一圈换成一次查表，O(n²) → O(n)。
填空只有三个：拿什么当 key、查什么、先查还是先存。

## 1. 配对：1 Two Sum

配对条件 `nums[i] + nums[j] == target`。存补数，后面的数拿自己来查：

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        remain_part = {}   # remain_value - index
        for idx in range(len(nums)):
            curr = nums[idx]
            if curr in remain_part:
                return [idx, remain_part[curr]]
            remain = target - curr
            remain_part[remain] = idx
```

契约是「存 `target - nums[i]`，查后来的 `nums[i]` 本身」，别拿 `remain` 去查。
[hash-table.md](../structures/hash-table.md) §4 那版反过来（存 `x`，查 `target - x`），两种都对，一题里别混。

## 2. 前缀和当 key：560

要配对的不再是单个元素，而是**一段**。把一段转成两个点：`sum(nums[i:j]) = pre[j] - pre[i]`。
于是「和为 k 的子数组有几个」=「扫到 `pre[j]` 时，前面有几个 `pre[i] == pre[j] - k`」——
还是 Two Sum，只是配对对象从元素换成了前缀和，表里存的从下标换成了次数。

```python
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        prefix_sum_counter = Counter()
        prefix_sum_counter[0] = 1      # 空前缀 pre[0] = 0
        prefix_sum = 0
        res = 0
        for elem in nums:
            prefix_sum += elem         # 此刻是 pre[j]
            if (prefix_sum - k) in prefix_sum_counter:
                res += prefix_sum_counter[prefix_sum - k]
            prefix_sum_counter[prefix_sum] += 1
        return res
```

- **`{0: 1}`** 是空前缀。不放它，从下标 0 开始的子数组配不上（`[1], k=1` → 0）。
- **为什么不能滑窗**：有负数，窗口和没有单调方向，「大了就缩左边」不成立。全是正数才能滑窗。
- **换 key 的变体**：974 存 `pre % k`；525 把 0 当 -1 后找和为 0 的最长子数组，要长度就存「第一次出现的下标」而不是次数 ——
  存什么等于题目要什么（[hash-table.md](../structures/hash-table.md) §1）。
- **搬到树上**：437 Path Sum III 也是这一招，前缀和沿根到当前节点那条路径累加，回溯时要把自己从表里减掉。
  仓库里 437 现在写的是双重 DFS 的 O(n²) 版。

## 3. 先查还是先存

一句话（560 pass2）：**查询那一刻，当前元素属不属于被查的那个集合？**

| 当前元素在不在被查的集合里 | 顺序 | 题 |
|---|---|---|
| 不在（配对要求 `i < j`） | 先查后存 | 1 / 560 |
| 在（窗口 `[l, r]` 含自己） | 先存后查 | 3 / 76 / 438 |
| 要看全局 | 两趟：全存完再查 | 128 / 242 / 138 |

顺序写反平时测不出来，只在**查询值恰好等于当前值**时炸：Two Sum 是 `target == 2 * x`（自己和自己配对），
560 是 `k == 0`（`[1], k=0` → 1，配上了 `i == j` 的空子数组）。写完先查后存的题，顺手测这一组。

## 4. key 是对象本身：138

138 复制带随机指针的链表，表是 `原节点 → 新节点`。key 必须是**节点本身**，不是 `val` —— `val` 会重复，
克隆要保的是指针的相等关系。而且必须两趟：`random` 可能指向后面还没建的节点，所以第一趟只建节点、填表，
第二趟 `next`、`random` 全变成查表。

## 5. 其余用法在结构页

| 题 | 用法 | 见 |
|---|---|---|
| 217 / 128 | 只要存在性，`set` 就够；128 还要入口剪枝 | [hash-table.md](../structures/hash-table.md) §3 §4 |
| 136 | `set` 当开关：没见过就加、见过就删，成对的抵消 | 第二个分支要 `elif`，两个独立 `if` 会刚加完就删 |
| 36 | 一个格子记三笔账，复合键 | [hash-table.md](../structures/hash-table.md) §5 |
| 49 | 范式当 key | [hash-table.md](../structures/hash-table.md) §5、[counting.md](counting.md) |
| 41 | 输入数组自己当表 | [hash-table.md](../structures/hash-table.md) §8 |
