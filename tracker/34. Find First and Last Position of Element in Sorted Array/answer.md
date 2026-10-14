两次闭区间二分：`nums[mid] < target` 则 `l = mid+1` 否则 `r = mid-1`，退出时 `l` = 第一个 ≥ target（左端点）；条件换成 `<=`，退出时 `r` = 最后一个 ≤ target（右端点）。

⚠ 左端点找完先判 `l >= n or nums[l] != target` → 不存在，返回 `[-1, -1]`；`l` 可能走到 `n`，不先判会越界。
