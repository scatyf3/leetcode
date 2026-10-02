每层决定**下一刀切在哪**：`for i in range(start, n)`，`s[start:i+1]` 是回文才 append 并 `dfs(i + 1)`；`start == n`（切完、没有剩余）才收。

⚠ 剩余部分不进 path，也不用判回文 —— 它是下一层的事。从单字符往上 merge 的思路，不同合并顺序会走到同一个切分。
