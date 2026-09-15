# 355. Design Twitter

我感觉system design类的题目
1. 不知道从何思考
2. 综合使用各种数据结构，比算法工程和吃时间
3. 是不是要留到后面专题刷，现在先把naive算法题吃熟

有任何comment和feedback吗？
1. 这题属于 LeetCode 的 Design 类，也叫 OOD 或数据结构设计，不同于system design
2. 怎么思考
列出每个 API，想清楚它读哪些状态、写哪些状态。
每份状态挑一个结构：要按 key 查就用 dict，要去重就用 set，按时间顺序追加就用 list。
找出最难的那一个操作，它通常就是一道你学过的经典题：
Twitter 的 getNewsFeed 对应合并 k 个有序列表
LRU 对应 hashmap + 双向链表
MedianFinder 对应两个 heap
3. 你今天的 bug 全出在杂活上，算法本身没问题. dictionary用defaultdict 能省下misc

不，但我核心的思路也想错了，我想的是维护个全局的堆，但这里标准用法是建立个随生随灭的堆，这里是我哪里没想清楚？

对啊，我想的其实是对的，每次发推触发newsfeed更新，比static get从用户体验和ttft延迟来说是更好的啊，不过这里应该是怎么简单怎么写吧？
1. 两个方案各自有tradeoff，口头讲
2. 代码优先保障正确

