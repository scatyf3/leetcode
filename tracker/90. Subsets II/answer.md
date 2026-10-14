78 + 先 `sort` + 同层去重：`if i > start and nums[i] == nums[i-1]: continue`。本层已经用这个值开过一棵子树，再开一棵是一模一样的。

⚠ 是 `i > start` 不是 `i > 0`：`i == start` 是本层第一个选择，必须放行，否则 `[2,2]` 出不来。set 去重不 sort 的话 `[1,2]` / `[2,1]` 两个 key 不同，照样重复。
