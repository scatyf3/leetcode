一趟扫描，哈希存**补数** `remain[target - nums[i]] = i`；每到一个数先查 `nums[i] in remain`，命中就返回 `[i, remain[nums[i]]]`，没中再存。

⚠ 契约是「存 `target - nums[i]`，查后来的 `nums[i]` 本身」—— 别拿 remain 去查。
