两种：
- **O(n²) DP**：`dp[i] = 以 nums[i] 结尾的 LIS 长度`，答案取 `max(dp)` 而**不是** `dp[-1]`（终点不固定）。初值全 1 = 「一次转移都没发生」时的真值。
- **O(n log n) 贪心+二分**：`tails[k] = 长度 k+1 的上升子序列里最小的结尾`，`bisect_left` 找位置，能接就 append 否则替换。答案 = `len(tails)`。

⚠ `tails` **不是**一条真实的子序列，长度可信、内容不可信。严格上升用 `bisect_left`，非严格用 `bisect_right`。
