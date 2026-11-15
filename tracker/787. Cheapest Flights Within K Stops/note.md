# 787. Cheapest Flights Within K Stops

idea很简单，正如我的分析，但是写的时候有坑

1. 自己迭代的变量千万不要和函数签名变量一致
2. 队列传cost
3. cnt-=1的一步，对其for _ in range(q_len)