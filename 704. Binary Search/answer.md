标准二分。推荐半开区间 `[l, r)` + `while l < r` 的写法：`nums[mid] < target` 时 `l = mid + 1`（mid 已排除），否则 `r = mid`（mid 可能是答案，不能减 1）。

⚠ 这个不对称正是二分最容易写错的地方。
