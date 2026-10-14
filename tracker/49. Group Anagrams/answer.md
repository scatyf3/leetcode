`"".join(sorted(s))` 当 key，字典 `key → list` 把同组的串收在一起，最后返回所有 value。

⚠ str 不可变，没有 `s.sort()`；要 `sorted(s)` 拿到列表再 `join`。
