定长窗口（长 `n = len(s1)`）：`need = Counter(s1)` 建好不动，`win` 每步进 `s2[r]`、出 `s2[r-n]`，比一次 `win == need`。

⚠ 认出**定长**：别按变长窗口写 `valid()` 又只推 r 不收 l —— `axxxb` 假阳、`aab` 假阴；也别在 need 归零时 `del` 键，移出窗口时还不回来。
