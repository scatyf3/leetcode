只看瓶颈：最多的任务（`max_cnt` 次）搭骨架，`(max_cnt-1)*(n+1) + num_max`（`num_max` = 并列最多的种数，站在尾巴上）；再和 `len(tasks)` 取 max（块塞满就没有空闲）。

⚠ 尾巴是 `+ num_max` 不是 `+ 1`。不想推公式就 heap 模拟：heap 存可发射的（按剩余次数），deque 存冷却中的。
