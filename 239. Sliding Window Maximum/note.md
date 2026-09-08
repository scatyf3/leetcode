# 239. Sliding Window Maximum

1. naive想法用heap，每次滑窗判断某个元素是否为堆顶，如果是的话则不管，然而假设[9,10,9]，滑走9的时候不管，会导致后面都错
2. counter，然而还是一个问题，counter能否移除cnt为0的kv pair，否则复杂度降不下来
3. agent，先写个naive deque，感觉会超时

---

1. 那就是维护一个max标量，然后每次移动队列update这个标量呗。但也不完全对，假设max被出队，还需要扫k重新找max。但至少这版能省一点？但还是超时
2. 对，感觉需要一个max chain，但是对非max，每个都要扫一次更新，那有回退了