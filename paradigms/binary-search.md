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

35 第一版最后一行写成 `return mid`，WA。
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

## 备注：另一套半开区间模板

`295. Find Median from Data Stream` 里手写的是半开 `[l, r)`：
`r = len(nums)` / `while l < r` / `r = mid`（不减一）/ `return l`。

它也对，但**规则和闭区间逐条不同**。同时背两套 = 每条规则都要二选一 = 记不住。
挑一套用熟，另一套读得懂就行。

## 相关

- `35. Search Insert Position` —— 模板 + `return l`
- `704. Binary Search` —— 模板 + `return -1`
- `295. Find Median from Data Stream` —— 半开区间版，坑记在 sol.py 底部
- `153. Find Minimum in Rotated Sorted Array` —— 比较对象换成 `nums[r]`
- `139. Word Break` —— 同一个思维模式：节点是缝不是字符
