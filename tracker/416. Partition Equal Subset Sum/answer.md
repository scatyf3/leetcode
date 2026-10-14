转成子集和：`target = total // 2`，维护集合 `reachable` = 已能凑出的和（≤ target），初始 `{0}`；每来一个 x 把所有 `s + x` 并进去，最后看 `target in reachable`。

⚠ `total` 为奇数直接 False；新和先收进 `new` 再 `reachable |= new`，边遍历边 `add` 会报 `Set changed size during iteration`。
