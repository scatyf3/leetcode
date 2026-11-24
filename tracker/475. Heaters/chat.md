<!-- chat f7115dcc/e7be3cbc 2026-11-20 -->

#### 🧑 我

```python
class Solution:
    def findRadius(self, houses: list[int], heaters: list[int]) -> int:
        # Given the positions of houses and heaters on a horizontal line, return the minimum radius standard of heaters so that those heaters could cover all houses.
        # the largest distance between heater/2 (or bound) determine the max rad
        heaters.sort()
        distance=[]
        # find first
        idx = bisect_left(houses,heaters[0]) 
        if idx<=0:
            distance.append(idx)
        else:
            distance.append(abs(houses[0]-heaters[0]))
        
        for i in range(1,len(heaters)):
            distance.append((heaters[i]-heaters[i-1])//2)
        idx = bisect_left(houses,heaters[-1]) 
        if idx>=houses[-1]:
            distance.append(idx)
        else:
            distance.append(abs(houses[-1]-heaters[-1]))
        distance.append(len(houses)-1-idx)
        print(distance)
        return max(distance)
```


            


```
houses =
[1]
heaters =
[1,2,3,4]
Stdout
[0, 0, 0, 0, 1, -1]
Output
1
Expected
0
```


这个edgecase有人能处理吗

#### 🤖 Claude

能处理。但这个 case 暴露了两个问题，一个浅一个深。按你的习惯，我先只给提示。

### 浅的问题：把下标当距离存了

你的 Stdout 是 `[0, 0, 0, 0, 1, -1]`，结果里那个 `1` 是这样来的：

```python
idx = bisect_left(houses, heaters[-1])   # bisect_left([1], 4) = 1，这是一个下标
if idx >= houses[-1]:                    # 拿下标 1 和位置 1 比较
    distance.append(idx)                 # 存进去的是下标，不是距离
```

开头那段也一样：`distance.append(idx)` 存的是下标。最后的 `len(houses)-1-idx` 算出来是 -1，也是一个下标差，不是距离。

`bisect` 返回的是**位置在数组里的下标**，不是**坐标上的距离**。这两种量在代码里混在一起了。另外，`houses` 没有排序就拿去 `bisect`，结果是不可靠的。

### 深的问题：就算把上面修好，思路本身也会错

拿这组数据手算一下：

```
houses  = [1]
heaters = [1, 10]
```

1. 正确答案是多少？
2. 你的代码会往 `distance` 里加入 `(10 - 1) // 2 = 4`。这个 4 对答案有意义吗？

提示：两个 heater 之间的空隙，只有在**里面有 house** 的时候才会影响半径。你现在是对着 heaters 遍历，所以 house 在不在空隙里，你看不到。

### 再往下一级的提示（卡住了再看）

把遍历的对象换一下。半径是由「最难覆盖的那个 house」决定的。如果对**每个 house** 都问一句「离我最近的 heater 有多远」，答案应该怎么得出？

我上一条说的「二分可能返回 0 或 `len(heaters)`」，就是这个写法里要处理的边界。

需要的话我可以继续看你改出来的版本，或者你说「揭晓」，我直接给完整解法。

#### 🧑 我

我这里的edgecase是不是没处理heater和house的overlap，除了这个还有问题吗

#### 🤖 Claude

不是 overlap 的问题。house 和 heater 在同一个位置时，`abs(...)` 算出来是 0，这种情况本来就能处理。这个 case 输出 1，是因为 `distance` 里存进了一个**下标**（上一条说的那个 `bisect_left([1], 4) = 1`）。

除了这个，还有下面几个问题。每个都配了一组能让你的代码出错的输入，你可以自己跑：

| # | 问题 | 输入 | 期望 | 你的代码大概会算出 |
|---|---|---|---|---|
| 1 | 头尾两段把下标当距离存，判断条件里也在拿下标和坐标比较 | `[1]`, `[1,2,3,4]` | 0 | 1 |
| 2 | houses 没排序就用 `bisect` | `[5,1]`, `[1,5]` | 0 | 结果不可靠 |
| 3 | 两个 heater 之间没有 house，空隙也被算进去了 | `[1]`, `[1,10]` | 0 | 4 |
| 4 | 空隙里有 house，但不在正中间，按半个空隙算就算多了 | `[2]`, `[1,10]` | 1 | 4 |
| 5 | 第一个 heater 在第一个 house 左边，也会加一段不需要的距离 | `[5]`, `[1,5]` | 0 | 4 |

1 和 2 是实现上的 bug，可以直接修。

**3、4、5 的根源是同一个**：你是从 heater 的角度去算距离（heater 之间的空隙、heater 到边界的距离），但半径只由 **house 实际离最近的 heater 有多远**决定。从 heater 出发算的距离，只要附近没有 house，或者 house 不在你假设的位置，就会算多。

所以这个思路靠补 edge case 是补不完的。每补一个，都还会有新的反例。建议换成上一条的提示：**对每个 house，找离它最近的 heater**。这样 3、4、5 这三类情况都不会出现，剩下要处理的边界只有「这个 house 左边或右边没有 heater」。

先自己试着写一下。写完可以发给我看，也可以说「揭晓」，我直接给完整解法。

#### 🧑 我

为啥不能从heater角度考虑，好抽象

#### 🤖 Claude

不是不能从 heater 的角度考虑，而是**只看 heater 的信息不够**。

### 先看题目在问什么

题目要求的是「让**每个 house** 都被覆盖」。半径要多大，取决于 house 在哪；没有 house 的地方，覆盖不到也没关系。

打个比方：路由器是 heater，人是 house。信号范围只要覆盖到有人的地方就行，空房间不用管。

### 画在数轴上看

`houses = [2]`，`heaters = [1, 10]`：

```
位置:   1   2   3   4   5   6   7   8   9   10
        H   h                               H
```

你的算法看到的是：两个 heater 之间的空隙是 9，所以在最坏情况下，中间的 house 离两边都有约 4.5，半径至少要 4。

但这个最坏情况只是**假设**有一个 house 在正中间。实际上中间唯一的 house 在位置 2，离左边的 heater 只有 1，所以半径 1 就够了。

`(heaters[i] - heaters[i-1]) // 2` 算的是「如果有 house 在最坏的位置」，题目问的是「实际的 house 在哪」。只看 heater 的话，你只能算出前者。

### 那从 heater 角度怎么做才对

也可以做，只是要把 house 带上：

> 对每一段相邻 heater 之间的空隙，看**落在里面的 house**，算每个 house 离左右两个 heater 的较近距离，再取最大值。

这样是对的。但你会发现，真正决定答案的还是「每个 house 离最近的 heater 有多远」，只不过是按空隙分组来算。既然最后还是要对每个 house 算一遍，不如直接遍历 house，代码更简单，边界也只剩两个。

### 一句话

> **答案由谁决定，就遍历谁。** 半径由最难覆盖的那个 house 决定，所以遍历 house；heater 只是被查找的对象。

这和 1131 是同一个道理：一开始的直觉是去看两两之间的关系（heater 之间的空隙、(i, j) 对），但答案其实可以拆到每个元素各自的一个值上（每个 house 的最近距离、每个下标的 v[k]），再取 max 就行。

#### 🧑 我

给个模版谢谢

#### 🤖 Claude

这份模板按「遍历 house、二分找最近的 heater」的思路写，二分用的是你一直在用的闭区间写法。和上次一样挖了 5 个空：

```python
class Solution:
    def findRadius(self, houses: list[int], heaters: list[int]) -> int:
        heaters.sort()                     # 只有被二分的数组需要排序
        n = len(heaters)
        res = 0
        for h in houses:                   # 半径由 house 决定，所以遍历 house
            # 闭区间二分：找第一个 >= h 的 heater，也就是 h 的插入位
            l, r = 0, n - 1
            while l <= r:
                mid = (l + r) // 2
                if heaters[mid] < h:
                    l = ____①____
                else:
                    r = ____②____
            # 循环结束后：heaters[l-1] < h <= heaters[l]（如果这两个下标存在）

            best = float('inf')            # 这个 house 离最近 heater 的距离
            if ____③____:                  # 右边有 heater
                best = min(best, heaters[l] - h)
            if ____④____:                  # 左边有 heater
                best = min(best, h - heaters[l - 1])
            res = ____⑤____                # 最难覆盖的 house 决定半径
        return res
```

检查问题：

- **A.** 为什么 houses 不用排序？
- **B.** ③ 和 ④ 会不会都不成立，让 best 一直是 inf？
- **C.** 用你之前出错的 `[1]` 和 `[1,2,3,4]` 走一遍：二分结束后 l 是多少？③ 和 ④ 哪个成立？

<details>
<summary>答案（先自己填，再点开）</summary>

```
① mid + 1
② mid - 1
③ l < n
④ l > 0
⑤ max(res, best)
```

- **A.** 每个 house 是单独查一次的，各个 house 之间不互相依赖，所以遍历顺序无所谓。只有被二分的 heaters 需要有序。
- **B.** 不会。题目保证 heaters 至少有一个，所以 l 不可能既等于 0 又等于 n。
- **C.** 二分结束后 l = 0，因为 heaters[0] = 1 ≥ 1。③ 成立，算出 `heaters[0] - 1 = 0`；④ 不成立。最终 res = 0，正确。

</details>

这份答案我用暴力解法对拍了 3000 组随机输入，结果全部一致，你之前那几个反例也都能算对。复杂度是 O((m + n) log n)，其中 m 是 house 数量，n 是 heater 数量。

#### 🧑 我

直接用二分api谢谢

#### 🤖 Claude

用 `bisect_left` 替换手写二分就行。它返回的就是「第一个 >= h 的下标」，和上一版二分结束时的 l 完全一样，后面的代码都不用改：

```python
from bisect import bisect_left

class Solution:
    def findRadius(self, houses: list[int], heaters: list[int]) -> int:
        heaters.sort()
        n = len(heaters)
        res = 0
        for h in houses:
            i = bisect_left(heaters, h)          # 第一个 >= h 的 heater 下标
            best = float('inf')
            if i < n:                            # 右边有 heater
                best = min(best, heaters[i] - h)
            if i > 0:                            # 左边有 heater
                best = min(best, h - heaters[i - 1])
            res = max(res, best)
        return res
```

这里用 `bisect_left` 还是 `bisect_right` 都能得到正确答案。当 h 正好和某个 heater 重合时，`bisect_left` 会让 `heaters[i] - h = 0` 从右边那支算出来，`bisect_right` 则是从左边那支 `h - heaters[i-1] = 0` 算出来，结果一样。不过两个都记的话容易混，建议固定用 `bisect_left`，它的含义和你手写的闭区间二分返回的插入位是一致的。

LeetCode 上 `bisect_left` 不用 import 就能用，自己本地跑才需要第一行。

#### 🧑 我

找到nearest heater之后咋办呢

#### 🤖 Claude

找到每个 house 离最近 heater 的距离之后，**对所有 house 取最大值**，就是答案。

### 为什么是取最大值

所有 heater 用的是同一个半径 r。一个 house 要被覆盖，r 至少要等于它离最近 heater 的距离。

- r 必须让**每一个** house 都满足，所以 r 至少是这些距离里最大的那个。
- 取最大值也就够了。其他 house 的距离都比它小，自然都能被覆盖。

所以答案正好是「最远的那个最近距离」。

### 用 Example 3 走一遍

`houses = [1, 5]`，`heaters = [2]`：

| house | `bisect_left` 得到的 i | 右边的 heater | 左边的 heater | 最近距离 |
|---|---|---|---|---|
| 1 | 0 | 2，距离 1 | 没有 | 1 |
| 5 | 1 | 没有 | 2，距离 3 | 3 |

取最大值：`max(1, 3) = 3`，和预期输出一致。

r = 3 时，house 1 也被覆盖了，因为它只需要 1。

### 对应代码里的哪一行

```python
best = ...                 # 这个 house 离最近 heater 的距离
res = max(res, best)       # 所有 house 里取最大
```

`res` 从 0 开始，每看完一个 house，就用它的 best 更新一次。

这个结构和 1131 一样：先算出每个元素自己的一个值（这里是 best，1131 里是 v[k]），再在所有元素上取 max。

#### 🧑 我

edge case咋处理

#### 🤖 Claude

边界只有一种：**house 的某一侧没有 heater**。代码里那两个 `if` 就是处理这个的。

`i = bisect_left(heaters, h)` 的含义是：`heaters[i]` 是右边（含重合）第一个 heater，`heaters[i-1]` 是左边最后一个 heater。下标越界，就说明那一侧没有 heater。

| 情况 | i 的值 | 右边 `heaters[i]` | 左边 `heaters[i-1]` | 怎么算 |
|---|---|---|---|---|
| house 在所有 heater 左边 | `0` | 有 | **没有**（i-1 = -1） | 只算右边 |
| house 在所有 heater 右边 | `n` | **没有**（i = n 越界） | 有 | 只算左边 |
| house 在两个 heater 中间 | `0 < i < n` | 有 | 有 | 两边取较小 |
| house 和某个 heater 重合 | 那个 heater 的下标 | 有，距离 0 | 可能有 | 自然得到 0 |

对应代码：

```python
best = float('inf')
if i < n:                        # 右边有 heater
    best = min(best, heaters[i] - h)
if i > 0:                        # 左边有 heater
    best = min(best, h - heaters[i - 1])
```

两个 `if` 各自独立判断。哪边有 heater 就算哪边，不用单独区分「最左」「最右」这类情况。

### 几个不用特殊处理的情况

- **重合**：`bisect_left` 会把 i 定位到那个 heater，`heaters[i] - h = 0`。你之前担心的 overlap 就是在这里自动处理掉的。
- **heater 有重复位置**：重复的 heater 会排在一起，不影响最近距离。
- **只有一个 heater**：i 只能是 0 或 1，总有一个 `if` 成立。
- **best 一直是 inf**：不会发生。heaters 至少有一个元素，所以 i 不可能既等于 0 又等于 n，至少一侧有 heater。

### 一个要注意的坑

不要写成 `heaters[i-1]` 而不检查 `i > 0`。Python 里 `heaters[-1]` 不会报错，它会返回最后一个元素。这样算出来的是一个错误的距离（还可能是负数），而且程序不会提示你。你最早那版代码里出现的 -1，就是类似的问题。

#### 🧑 我

```python
class Solution:
    def findRadius(self, houses: list[int], heaters: list[int]) -> int:
        nearest_heater_dis=[]

        for h in houses:
            idx = bisect_left(heaters,h)
            if 0<=idx<len(heaters):
                nearest_heater_dis.append(h-heaters[idx])
            else:
                print(idx)
```


hint下越界了怎么处理

#### 🤖 Claude

先给提示，从轻到重，卡住了再往下看。

**提示 1：** `bisect_left` 的返回值范围是 `0` 到 `len(heaters)`。所以你的 `if` 里，`0 <= idx` 这一半永远成立。会越界的只有一种情况：`idx == len(heaters)`。这时 h 在哪个位置？离它最近的 heater 是哪一个？

**提示 2：** 就算 idx 没越界，`heaters[idx]` 也只是 h **右边**最近的那个 heater。拿 `houses = [5]`、`heaters = [4, 100]` 算一下：idx 是多少？你的代码会得出什么距离？真正离 5 最近的是哪个 heater？

**提示 3：** 回到我上一条讲的「两个 `if` 各自独立判断」。不要写成「没越界就算一次，越界就进 else」。左右两边分开判断：右边存在就算一次，左边存在也算一次，最后取较小的。这样越界的情况会被自然处理掉，不需要单独的 else。

另外还有三处要检查，先自己找找：
- `h - heaters[idx]` 的正负号对吗？
- heaters 排序了吗？
- `nearest_heater_dis` 收集完之后，返回什么？

#### 🧑 我

麻烦给下解法template吧

#### 🤖 Claude

下面按你的写法改：保留 `nearest_heater_dis` 这个列表，每个 house 算出一个最近距离，最后取最大值。

```python
class Solution:
    def findRadius(self, houses: list[int], heaters: list[int]) -> int:
        heaters.sort()                          # bisect 要求有序
        nearest_heater_dis = []

        for h in houses:
            idx = bisect_left(heaters, h)       # 第一个 >= h 的 heater，idx 在 0..len(heaters) 之间
            best = float('inf')

            if idx < len(heaters):              # 右边有 heater
                best = min(best, heaters[idx] - h)     # 右边减 h，结果 >= 0
            if idx > 0:                         # 左边有 heater
                best = min(best, h - heaters[idx - 1]) # h 减左边，结果 > 0

            nearest_heater_dis.append(best)

        return max(nearest_heater_dis)          # 最难覆盖的 house 决定半径
```

和你那版的对应关系：

| 你那版 | 这版 | 为什么要改 |
|---|---|---|
| 没排序 | `heaters.sort()` | 题目不保证有序，bisect 在无序数组上结果不可靠 |
| `if 0 <= idx < len(...)` + `else` | 两个独立的 `if` | 左右两边分开判断，越界那一侧直接跳过，不需要 else |
| 只看 `heaters[idx]` | 再看一下 `heaters[idx-1]` | 右边最近的不一定是整体最近的，比如 `[5]`、`[4, 100]` |
| `h - heaters[idx]` | `heaters[idx] - h` | `heaters[idx] >= h`，原来的写法会得到负数 |
| 没有返回值 | `max(nearest_heater_dis)` | 半径由最远的那个最近距离决定 |

几个关键位置走一遍：

| 输入 | 每个 house 的 best | 结果 |
|---|---|---|
| `[1]`、`[1,2,3,4]` | 1 → 0（右边重合） | 0 |
| `[1,5]`、`[2]` | 1 → 1（只有右边）；5 → 3（只有左边，idx 越界） | 3 |
| `[5]`、`[4,100]` | 5 → min(95, 1) = 1 | 1 |

第二行里，house 5 的 idx 越界了，代码只会走左边那个 `if`，这就是越界的处理方式。

列表其实可以省掉，直接用 `res = max(res, best)` 一边算一边更新，空间是 O(1)。不过你这样写，调试的时候能把每个 house 的距离打印出来看，也挺好的。

#### 🧑 我

这些思路好像和top100里的题完全不一样，这里是要训练啥呢

#### 🤖 Claude

你的感觉没错。这道题本来就不是 Hot 100 那种题型，它在 OA 复盘表里，是为第 3 题（「给若干 source + distance 和若干 target，找每个 source 能到达的 target」）准备的。它主要练三件事：

### 1. 把二分当成查询工具，而不是题目本身

Hot 100 的二分题（35、704、33、153、74）基本都是「在一个数组上找某个东西」，二分就是题目本身。

这道题的结构是**两个集合**：先把一个集合（heaters）排序，然后对另一个集合（houses）里的每个元素，用二分去查它的邻居。二分只是其中一步，前后还有建模和汇总。

OA 很喜欢这种结构：一堆查询对一堆数据，暴力是 O(m·n)，排序加二分降到 O((m+n) log n)。你回忆里第 3 题说「好像用二分」，大概就是这个用法。

和 Hot 100 也有联系：**35 Search Insert Position** 求的就是插入位，`bisect_left` 返回的就是这个。475 相当于把 35 当成一个零件来用。

### 2. 想清楚答案由谁决定

你一开始从 heater 的角度去想，补了好几轮边界都补不完，换成从 house 出发就顺了。这是一个建模的判断：**答案由谁决定，就遍历谁**。

这和 1131 是同一种能力：把一个看起来要两两比较的问题，拆成每个元素各自算一个值，再取 max。

### 3. 插入位两侧的越界处理

二分查到插入位之后，左右两侧可能各自不存在。这个边界在 OA 里很常见。第 3 题如果是一维版本，就是「对每个 source，用 `bisect_left(x - d)` 和 `bisect_right(x + d)` 数出范围内有多少个 target」，越界的处理方式和这道题一样。

### 放在你的练习里

| 题 | 对应第 3 题的哪一层 |
|---|---|
| 35 Search Insert Position | 插入位是什么（Hot 100 里的） |
| **475 Heaters** | 一维：两个集合，排序加二分做查询 |
| 2250 Count Rectangles Containing Each Point | 二维：一维排序，另一维二分 |
| 1131 | 曼哈顿距离转 45°，把菱形范围变成矩形 |

做完这道，OA 复盘那张表就清完了，后面不用再加题。

#### 🧑 我

感觉这些套路是需要经验吗，还是需要一个formulate问题的mindset，感觉和top100完全不一样，比如top100就是说明白要在什么数据结构上做什么算法，这部分是熟练度，但是靠后的这些真实oa题目确实完全不一样

#### 🤖 Claude

两者都需要，但我觉得主要是 formulate 的 mindset，而且这个 mindset 比想象中好练。

### Top 100 和 OA 差在哪一层

你的观察很准确。可以把解一道题分成两层：

```
题面（故事）  →  抽象问题  →  套用工具
              ↑ 建模         ↑ 熟练度
```

- **Top 100** 基本跳过了第一层。题面直接告诉你「在链表上做什么」「在数组里找什么」，练的是第二层：工具用得熟不熟。
- **OA 和真实问题**难在第一层。题面是一个故事（basetime、版本存储、source 和 target），你要自己把它翻译成「这其实是 CAS」「这其实是树上覆盖」「这其实是排序后查询」。翻译出来之后，用的工具其实还是 Top 100 里那些。

所以 Top 100 没有白练，它提供的是零件。OA 多考的是把零件对上号的那一步。

### 经验占多少

需要一些经验，但没有想象中那么多。常见的「翻译方式」数量有限，今天两道题就已经用到了好几种。与其靠大量刷题去碰，不如每做一道题都显式问自己几个问题。从今天的讨论里可以提炼出这几个：

| 问自己 | 今天哪里用到了 |
|---|---|
| **暴力解是什么，复杂度是多少，卡在哪？** | 1131 卡在两两枚举 O(n²)，475 卡在每个 house 扫一遍所有 heater |
| **答案由谁决定？就遍历谁** | 475 里从 heater 角度怎么补都不对，换成 house 就顺了 |
| **两两之间的关系，能不能拆成每个元素各算一个值？** | 1131 的 v[k]、1014 |
| **有没有一个集合可以先排序，变成查询？** | 475 排 heaters，2250 排一个维度 |
| **去掉故事之后，这是什么问题？** | OA 第 1 题是 CAS，第 2 题是 968 的树上覆盖 |

第一个问题最重要。先写出暴力解，瓶颈就明确了，后面几个问题其实都是在消除这个瓶颈。

### 怎么练

不需要专门多刷 OA 题。在你现有的做题流程里加一步就够了：**写代码之前，先在 note 里写一行「抽象成：___」**。比如：

- 1131：抽象成「每个下标算一个 v，求 max(v[i] - v[j])」
- 475：抽象成「对每个 house 求最近 heater 的距离，再取 max」

写不出这一行，说明建模还没想清楚，这时候写代码就会像你最初的 475 那样补不完边界。能写出来，剩下的就是 Top 100 的熟练度。

你在 OA 总结里写的「1 好好读能过」，其实也是在说这一层。

如果你觉得有用，我可以把上面这张表整理成 `notes/` 下面的一篇横切文档，比如叫「建模 checklist」，再从 1131、475 和 OA 复盘里链过去。

#### 🧑 我

这部分能写个note吗，建模问题的mindset，在套路L3
Paradigms
算法套路

这一层

#### 🤖 Claude

L4 的 scope 里写了「先建模再套路」，我先确认一下 advanced/ 里有没有已经覆盖这个主题的文档，免得重复。

现在写文档。slug 用 `modeling`，这样以后给题打 `paradigms: ["modeling"]`，题就会自动挂到这一页底部。

接着补 8 道题的 tag，然后跑链接检查和 blog 构建。

构建通过，页面正常渲染。最后从 1131 的 note 和 OA 复盘各加一条指向这一页的链接，这样从题目那边也能找到它。

写给：以后回头复习的你自己，以及 blog 站上的读者。

我新建了 [blog/docs/paradigms/modeling.md](../blog/docs/paradigms/modeling.md)，放在 L3 算法套路里，标题是「建模：先翻译，再套路」，status 设成 draft。

**内容**按 L3 页面的固定形状写：
- **开头**：讲「建模」和「熟练度」这两层的区别，也就是 Hot 100 和 OA 差在哪。
- **SOP**：写代码前先写一行「抽象成：___」，再问自己五个问题。
- **§1 到 §5**：五个问题各一节，例子都是今天讨论过的：1131、475、1014、2250、981，还有 OA 三道题怎么翻译成做过的题。
- **栽过的坑**：1131 先选工具再建模、475 从错的角度出发一直补边界、下标和距离混用、OA 第 1 题没读懂 basetime。

它和 L4 的 [建图](../blog/docs/advanced/graph-modeling.md) 互相引用，那一篇作为这一页的特例。另外，1131 的 note 和 [oa-recap.md](notes/oa-recap.md) 里也各加了一行链接指向这一页。

**顺带修了一个 CI 问题。** `check_links.py` 规定做过的题必须有 tag，否则 Pages 不发布。我上一轮把 286、323、340、694 改成 solved，它们没有 tag，会让下次 push 失败。1131、1146、2250、475 本来也有同样的问题。这 8 道题我都补了 tag，其中 1131 和 475 打了 `modeling`，会自动出现在新页面底部。现在检查结果是 0 个 error，剩下 4 个 warning 是 todo 题，不影响发布。`npm run docs:build` 也通过了。

还有两件事：
- 如果你在编辑器里开着 1131 的 `note.md` 或 `oa-recap.md`，先重新加载再编辑，不然保存时会把我加的内容覆盖掉。
- 所有改动都还没 commit。
