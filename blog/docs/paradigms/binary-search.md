---
title: 二分查找
status: draft
order: 3
related: [/python/bisect-sorted]
---

# binary-search

## 模板：闭区间 [l, r]

```python
l, r = 0, len(nums) - 1
while l <= r:
    mid = (l + r) // 2
    if nums[mid] < target:
        l = mid + 1          # mid 已排除，跨过去
    elif nums[mid] > target:
        r = mid - 1          # mid 已排除，跨过去
    else:
        return mid           # 命中：有 nums[mid] == target 这个检查背书
# 出了循环 = 没找到
```

**两类题只差最后一行**（5 万组随机对拍，两边都零错）：

```python
return -1     # 704. Binary Search        —— 找不到
return l      # 35. Search Insert Position —— 该插入的位置
```

不用背两个模板。「找元素」和「找插入位」是同一个循环的两种收尾。

## 唯一的记忆锚点

> **`l` / `r` 是状态量，`mid` 是过程量。循环外只能从状态量读答案。**

循环不变量全程只说一件事：

```
答案一定在还没排除的区间 [l, r] 里
```

这句话里**没有 mid**。所以循环外出现 `mid` 一定是错的。

## 退出时 l 和 r 各指什么

`l <= r` 退出 ⟺ 区间空掉 ⟺ **`l == r + 1`**，两者恰好把答案那条缝夹在中间：

```
_ 1 _ 3 _ 5 _ 6 _        target = 2
    ↑ ↑
    r l                  r = 最后一个 < target 的下标
                         l = 第一个 >= target 的下标  ← 插入的缝
```

要缝右边的编号 → `return l`。

**`r` 初值取 `n-1`，`l` 照样能走到 `n`**（全部元素都小于 target 时）。
所以闭区间模板不需要为「插到末尾」做任何特殊处理 —— 答案空间靠 `l` 增长覆盖，
不靠 `r` 的初值。（半开区间那套才需要 `r = n`，见文末。）

## 踩过的坑：`return mid`

LC 35 第一版最后一行写成 `return mid`，WA。
`[1,3,5,6], target=2` 期望 `1`，返回 `0`。

**不是 edge case，是每个「没找到」的用例都错，且恒定偏 1。**
退出时 `l == r+1`，若 mid 在循环体末尾重算过：

```
mid = (l + r)//2 = (2l - 1)//2 = l - 1
```

`return mid` ≡ `return l - 1`。
`[1,3,5,6], 0` 那组更露骨：退出时 `l=0, r=-1`，`mid = -1` ——
已经不是「偏一格」，是这个值压根没有下标语义
（Python 里 `-1` 还是合法下标，不报错，更阴险）。

### 同一个 `return mid` 为什么一个对一个错

```python
    else:
        return mid    # ✅ 上一行刚验证过 nums[mid] == target，有证据
return mid            # ❌ 没有任何东西验证过它
```

循环内那个的正确性来自**刚做完的检查**，跟二分结构无关（换线性扫描也对）。
循环外那个只是最后一次赋值的残值 ——「空区间的中点」不存在。

### 别靠直觉猜 mid 在缝的哪边

三万组随机，闭区间写法退出后的 `mid`：

```
mid 在循环体末尾重算  →  mid - l 恒为 -1        （每次都偏，一交就 WA）
mid 在循环开头算      →  mid - l ∈ {0, -1}     （时对时错，最难查）
```

取决于最后一次迭代走了哪个分支。**`mid` 在循环外没有稳定含义** ——
第二种才是真正危险的，它能过一部分用例。

顺带：`mid` 只在循环开头算一次就好。放在循环体末尾会多算一次
（在空区间上），那次的结果就是上面那个害人的残值。

## 写完 10 秒自检

只看三个位置：

1. **收缩那两行** —— 都跨过 mid 了吗？(`mid+1` / `mid-1`) 漏一边会死循环。
2. **循环条件** —— 闭区间配 `l <= r`。写成 `l < r` 会漏掉区间只剩一格的情况。
3. **最后一行** —— `return -1` 还是 `return l`？出现 `mid` 就错。

## 变体

```python
# 有重复元素、要第一个/最后一个：不能用 == 提前 return，
# 命中时也得继续收缩，把等号并进某一边
r = mid - 1   # 相等也往左收 -> 收敛到 bisect_left（第一个 >= target）
l = mid + 1   # 相等也往右收 -> 收敛到 bisect_right（第一个 > target）
# 两种都是退出后 return l

# 153. Find Minimum in Rotated Sorted Array
# 比较对象换成 nums[r]（跟右端点比），不是跟 target 比
```

## 统一视角：所有二分都在找 F → T 的那条缝

上面的模板、变体、153，其实是同一个循环换了不同的判定条件。把每个下标贴上 F / T：

```python
l, r = lo, hi
while l <= r:
    mid = (l + r) // 2
    if pred(mid):
        r = mid - 1          # mid 是 T -> 缝在 mid 或它左边
    else:
        l = mid + 1          # mid 是 F -> 缝在 mid 右边
return l                     # 第一个 T
```

### 不变量只有两句

```
l - 1 是 F      （初始 l = lo，把 lo-1 当成虚拟的 F）
r + 1 是 T      （初始 r = hi，把 hi+1 当成虚拟的 T）
```

依据：`l = mid + 1` 只在 mid 是 F 时发生，所以新的 `l - 1` 就是那个 F；`r` 同理。
退出时 `l == r + 1`，两句说的是**相邻两格**：`l-1` 是 F，`l` 是 T，`l` 就是那条缝。

> `return l` 不是记出来的，是两句不变量在退出那一刻拼起来的结果。

### 各题的 pred 是什么

| 题 | 下标空间 | pred(i)（T 的条件） | 返回 |
|---|---|---|---|
| 35 | `[0, n-1]` | `nums[i] >= target` | `l` |
| 704 | `[0, n-1]` | 同 35，外加 `==` 提前 return | `-1` |
| 744 | `[0, n-1]` | `letters[i] > target` | `letters[l]`，`l == n` 时绕回 `[0]` |
| 34 左界 / 右界 | `[0, n-1]` | `>= target` / `> target` | `l` / `r`（右界 = 最后一个 `<=`，也就是缝左边那格） |
| 153 | `[0, n-1]` | `nums[i] <= nums[-1]`（落在小段） | `nums[l]` |
| 287 | **值** `[1, n]` | `count(<= v) > v` | `l` |
| 162 | `[0, n-2]` | `nums[i] > nums[i+1]`（这一步是下坡） | `l` |

拿到新题先问：**F / T 分别是什么？**说得出来，剩下的就是上面那段循环。

### 162 为什么最抽象：pred 不单调

前面几题的 pred 都是**单调**的（FFF…TTT），只有一条缝，`l - 1 是 F` 能推出 l 左边全是 F。

162 的 pred 是「这一步下坡」，数组有好几个峰时，它长这样：

```
nums:   1  3  2  4  1
pred:   F  T  F  T  (n-1 是虚拟的 T)
```

有好几条缝，不变量只能保证 `l-1` 那**一格**是 F，管不到更左边的格子。那为什么还能二分？

> **两端标签不同，中间必有一处翻转。**左端 F、右端 T，从左走到右总得在某一步从 F 变成 T。

二分每次扔掉一半，但始终保持「左边界外是 F、右边界外是 T」，所以剩下的区间里一定还藏着至少一条缝。
这和数值分析里的二分法求根是一回事：`f(a) < 0`、`f(b) > 0`，中间一定有根，砍一半，留下仍然异号的那一半。

> **二分要的不是单调，是端点异号。**单调只是让缝变成唯一的那条。

162 的两个端点：
- `l = 0`：`nums[-1] = -∞`，左边界外是 F（上坡）
- `r = n-2`：`r+1 = n-1`，而 `nums[n] = -∞`，`n-1` 一定是 T（下坡）

`r` 初值取 `n-2`，一是 `mid + 1` 不会越界，二是让 `r + 1 是 T` 从一开始就成立。

### 同类练习（「pred 不单调 / 和邻居比」）

| 题 | 题单 | 跟 162 的关系 |
|---|---|---|
| 1901. Find a Peak Element II | leetcode必吃榜 | 162 的二维版：对行二分，每行取最大值再和上下比 |
| 852. Peak Index in a Mountain Array | agent补充 | 162 的特例，只有一个峰，pred 退化成单调的。拿来热身 |
| 540. Single Element in a Sorted Array | agent补充 | 和配对的那个邻居比，自己想 F / T 怎么定义 |
| 1095. Find in Mountain Array | — | 先用 852 找峰，再在两边各跑一次普通二分 |

## 备注：另一套半开区间模板

`295. Find Median from Data Stream` 里手写的是半开 `[l, r)`：
`r = len(nums)` / `while l < r` / `r = mid`（不减一）/ `return l`。

它也对，但**规则和闭区间逐条不同**。同时背两套 = 每条规则都要二选一 = 记不住。
挑一套用熟，另一套读得懂就行。

## 相关

- [35. Search Insert Position](https://github.com/scatyf3/leetcode/blob/main/tracker/35.%20Search%20Insert%20Position/note.md) —— 模板 + `return l`
- [704. Binary Search](https://github.com/scatyf3/leetcode/blob/main/tracker/704.%20Binary%20Search/note.md) —— 模板 + `return -1`
- [295. Find Median from Data Stream](https://github.com/scatyf3/leetcode/blob/main/tracker/295.%20Find%20Median%20from%20Data%20Stream/sol.py) —— 半开区间版，坑记在 sol.py 底部
- [153. Find Minimum in Rotated Sorted Array](https://github.com/scatyf3/leetcode/blob/main/tracker/153.%20Find%20Minimum%20in%20Rotated%20Sorted%20Array/note.md) —— 比较对象换成 `nums[r]`
- [162. Find Peak Element](https://github.com/scatyf3/leetcode/blob/main/tracker/162.%20Find%20Peak%20Element/note.md) —— pred 不单调，靠端点异号
- [744. Find Smallest Letter Greater Than Target](https://github.com/scatyf3/leetcode/blob/main/tracker/744.%20Find%20Smallest%20Letter%20Greater%20Than%20Target/note.md) —— 找右缝，`l == n` 绕回
- [34. Find First and Last Position of Element in Sorted Array](https://github.com/scatyf3/leetcode/blob/main/tracker/34.%20Find%20First%20and%20Last%20Position%20of%20Element%20in%20Sorted%20Array/note.md) —— 两条缝，左界 `return l`、右界 `return r`
- [287. Find the Duplicate Number](https://github.com/scatyf3/leetcode/blob/main/tracker/287.%20Find%20the%20Duplicate%20Number/note.md) —— 在值上二分，不是在下标上
- [139. Word Break](https://github.com/scatyf3/leetcode/blob/main/tracker/139.%20Word%20Break/note.md) —— 同一个思维模式：节点是缝不是字符
