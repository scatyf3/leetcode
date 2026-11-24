<!-- chat f7115dcc/5a76d876 2026-11-20 -->

#### 🧑 我

#45 Jump Game II 这我好像解过了吧，都1.5熟练度了

#### 🤖 Claude

对，你做过。我刚看了文件夹：

- [sol.py](45.%20Jump%20Game%20II/sol.py) 是你 10/13 写的版本：先建 reachable 表，再做 DP，复杂度 O(n·m)。
- [optimal.py](45.%20Jump%20Game%20II/optimal.py) 是按层 BFS 的贪心版本。
- `meta.json` 里 familiarity 是 1.5，但 **status 还是 `todo`**，应该是当时忘了改。我上一条是看了 status 才说它没做，判断错了。

不过对 OA 第 2 题来说，有用的是**贪心版本**，不是 DP 版本。你 [note.md](45.%20Jump%20Game%20II/note.md) 里最后停在「这样如何保障一定 cover 答案呢……很神奇」，看起来贪心那部分当时还没完全消化。optimal.py 也不确定是不是你自己写的。

所以这道题不用当新题做，在小做日**空白重写一遍贪心版本**就够了，十分钟左右。要求是能自己说清楚为什么每一层只需要记住「最远能到哪」。说得清楚就算过，然后对照第 2 题想一下：「累计代价快超过 t 就存一个全量」，和「这一层走到边界就必须再跳一步」是同一个动作。

这样 OA 复盘需要另外练的就只剩 475 Heaters 一道。

要我把 45 的 status 改成 solved 吗？改完我会调一下 `/api/sync`，让看板同步。

#### 🧑 我

对的，你检查下有啥解过的mark as solved

#### 🤖 Claude

有 6 道 todo 的题 sol.py 里有代码：286、323、340、45、694、77。我先看看它们是不是真的写完了。

这几份代码要先跑一下，确认真的是对的。694 的 DFS 没有先标记起点，我重点对拍一下。

6 道全部对拍通过。下面把它们改成 solved，然后同步看板。

我把 6 道题改成了 solved。改之前每道都和暴力解法或另一份实现跑了几百组随机输入，结果全部一致。

| 题 | 用哪份代码判定 | 备注 |
|---|---|---|
| 45 Jump Game II | sol.py（DP） | 和 optimal.py 的贪心版本结果一致 |
| 286 Walls and Gates | sol.py | 多源 BFS |
| 323 Number of Connected Components | sol2.py（并查集） | sol.py 是你笔记里说的那个错误的 list of set 写法，没用它 |
| 340 Longest Substring with At Most K Distinct | sol.py | 滑动窗口 |
| 694 Number of Distinct Islands | sol.py | DFS 没有先标记起点，靠邻居绕回来才把起点加进去。结果是对的，但不是标准写法，你笔记里已经记了 |
| 77 Combinations | sol.py | 回溯 |

每个 `meta.json` 只改了 status 这一行，其他字段没动。看板已经调过 `/api/sync`，确认这 6 道显示为 solved。

**这几道我没动：**
- **还是 todo，因为 sol.py 是空的**：1851、271、475、707、785，确实还没做。
- **review 状态**：295、98。这是你有意标记的待复习状态，我没碰。

改动还没 commit。

#### 🧑 我

https://leetcode.com/problems/heaters/description/

这道题里面所有的heater会在house之间吗，还是能在之外eg houses=[1,5] , heaters=[6]

#### 🤖 Claude

可以在外面。题目对 heater 的位置只限制了 `1 <= heaters[i] <= 10^9`，没有要求它落在 houses 的范围里。

你举的例子 `houses = [1, 5]`、`heaters = [6]`，答案是 5，因为 house 1 到 heater 6 的距离是 `|1 - 6| = 5`。官方 Example 3 就是这种情况：`houses = [1, 5]`、`heaters = [2]`，输出 3。heater 在中间，离 house 5 远一些。

另外两个题面细节要注意：
- **两个数组都不保证有序**，要用二分得自己先排序。
- **多个 heater 可以在同一个位置**，一个 heater 也可以和某个 house 在同一个位置，这时那个 house 的距离是 0。

你问这个，应该是在想二分边界。给个提示，不讲解法：对每个 house 在 heaters 里二分查找时，查到的位置可能是 0，也可能是 `len(heaters)`。这就对应「这个 house 左边没有 heater」或「右边没有 heater」。写的时候想好这两种情况怎么处理就行。
