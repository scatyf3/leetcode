# 76. Minimum Window Substring

很烦，是对LC 567的放缩
1. 扫r，一旦valid收l
2. 判断valid，LC 567 有个轮椅是py counter的高级特性，这里naive的做法是维护一个missing的int，无条件更新counter，只在当前str在target str的counter里边missing
3. 所以相当于把naive的counter O(26)比较变成O(1)


pass2
1. counter的语意是need，所以入窗口-，出窗口+
2. 先结算在缩左边界，没有off by one
3. bestl/r/len的哨兵

```python
best_len = lens + 1                # ⑤ 哨兵
best_l, best_r = 0, -1             # ⑤ -1 = 还没找到
```