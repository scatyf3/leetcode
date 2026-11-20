# OA 复盘:时间戳 KV / 版本存储 / 范围查询

适用:下一场 OA 之前过一遍。同类题在看板「专题 → OA 复盘」里,顺序 981 → 968 → 2250。

---

## 题目回忆(原话)

1. given key，value， basetime（？），对比上一次的edit时间，类似time key value pair
   但是这个b有啥用呢，basetime比上一轮的iteration time这样
2. 文件版本管理，keep一些node，prune一些，让全部的node都能在t的cost里重构
3. given若干source+distance和若干target的坐标，搜每个source在distance能达到的target，好像用二分。

## 总结(原话)

- 感觉1 好好debug好好读能过，23还不熟悉
- 最重要的是平台熟悉度，怎么print debug，怎么看，或者自己构建用例
  先做 Sample Assessment，然后去各种题库试试

> 下次 OA 前先做一遍平台的 Sample Assessment,确认三件事:print 输出在哪看、怎么跑自定义用例、提交前能不能看到隐藏用例的报错。

---

## 三道题的考点和同类题

三道题在 LeetCode 上都没有原题,但每道都有考点相同的题可以练。

### 1. 带时间戳的 key-value store

basetime 应该是乐观并发控制(compare-and-set)里的版本号:

- basetime 表示「我是基于哪个时刻读到的值来改的」。
- 写入时比较:如果这个 key 的上次修改时间 ≤ basetime,说明你读完之后没人改过,允许写入,并把修改时间更新为本次时间。
- 如果上次修改时间 > basetime,说明中间有人改过,你是基于旧值在改,要拒绝或者报冲突。

HTTP 的 `If-Unmodified-Since` 和 DynamoDB 的条件写入都是这个思路。没看到原题,所以这只是推测,要对照题面确认。

| 题 | 练什么 |
|---|---|
| [981 Time Based Key-Value Store](../981.%20Time%20Based%20Key-Value%20Store/note.md) | 按时间戳存多个版本,二分查某个时刻的值。最接近原题 |
| 1146 Snapshot Array | 版本号 + 二分 |
| 1797 Design Authentication Manager | 比较时间决定操作是否生效,带 TTL |
| 2034 Stock Price Fluctuation | 同一时间戳会被覆盖更正 |

### 2. 版本存储:每个版本都能在 cost ≤ t 内重建

数据库里讲的存储和重建代价的权衡:部分版本存全量,其余存 delta,要求任意版本从最近的全量版本开始、应用 delta 的总代价不超过 t。

- 版本是一条链:从前往后贪心,累计代价快超过 t 就存一个全量。
- 版本是一棵树:自底向上贪心或树形 DP。在子树里,离最近全量祖先最远的未覆盖距离一旦达到 t,就必须存当前节点。

| 题 | 练什么 |
|---|---|
| [968 Binary Tree Cameras](../968.%20Binary%20Tree%20Cameras/note.md) | 自底向上贪心覆盖,套路几乎一样。note 里有贪心染色 → DP → 推广到本题的完整推导 |
| [45 Jump Game II](../45.%20Jump%20Game%20II/note.md) | 链上的版本,区间覆盖贪心 |
| 1326 Minimum Number of Taps to Open to Water a Garden | 同上,区间覆盖 |

### 3. source + distance 找能到达的 target

| 题 | 练什么 |
|---|---|
| 475 Heaters | 一维版本,排序 + 二分,入门 |
| [2250 Count Number of Rectangles Containing Each Point](../2250.%20Count%20Number%20of%20Rectangles%20Containing%20Each%20Point/note.md) | 二维范围查询,一维排序、另一维二分,和原题结构最像 |
| 1828 Queries on Number of Points Inside a Circle | 点在不在范围里的暴力版 |
| 1131 Maximum of Absolute Value Expression | 曼哈顿距离的 u = x+y、v = x−y 转换 |
| 3102 Minimize Manhattan Distances | 同上 |
