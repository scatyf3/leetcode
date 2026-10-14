判据 `letters[i] > target` 把数组划成 F…F T…T，闭区间 `[l, r]` 找**第一个 T**：mid 是 T 则 `r = mid-1`，否则 `l = mid+1`，退出时 `l` 就是答案下标。

⚠ 全是 F 时 `l` 走到 `n`，要回绕返回 `letters[0]`（即 `letters[l % n]`）。
