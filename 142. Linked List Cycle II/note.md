# 142. Linked List Cycle II

### 思路

设fast/slow相遇点，则head-环起点距离为a，环起点-相遇点b，相遇点-环起点 c

递推关系 
1. fast: a+b+n(b+c)
2. slow: a+b

则有2(a+b)=a+b+n(b+c) => a = c+(n-1)(b+c)

这里的含义是，若把其中一个指针拿回head，都迭代走一个step，则相遇点就是交点

## 细节

双指针比较烦，fast本地，fast next都要有为none的edge case处理