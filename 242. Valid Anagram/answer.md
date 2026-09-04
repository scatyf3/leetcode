一张计数表：扫 s 时 `+1`，扫 t 时 `-1`，最后全为 0 就是异位词。或者直接 `Counter(s) == Counter(t)`。

⚠ 先比长度剪枝。用 `Counter` 或 `dict.get(c, 0) + 1` 消掉 if-else。
