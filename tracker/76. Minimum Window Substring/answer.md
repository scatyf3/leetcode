滑窗 + `cnt = Counter(t)` 当 need：右扩入窗 `cnt[c] -= 1`，一旦所有 `cnt ≤ 0`（覆盖了 t）就**先结算最短再收左** `cnt[s[l]] += 1; l += 1`，直到不再覆盖。

⚠ `for r in range(...)` 里别再手动 `r += 1`；先结算再缩左边界，不会 off by one。
