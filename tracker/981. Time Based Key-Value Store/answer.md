每个 key 存两条平行数组 `times / vals`（set 的 timestamp 递增，append 即有序）；get 时闭区间二分搜缝 `P = times[mid] <= timestamp`：T 则 `l = mid+1`，否则 `r = mid-1`，返回 `vals[r]`。

⚠ 退出时 `r` = 最后一个 ≤ timestamp；`r < 0` 说明全比它晚，返回 `""`。
