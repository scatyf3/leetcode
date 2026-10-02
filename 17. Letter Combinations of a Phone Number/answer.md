按位填：第 `pos` 层枚举 `digits[pos]` 对应的字母，`pos == len(digits)` 时 `res.append("".join(cur))`。

⚠ 空输入要特判返回 `[]` —— 不判的话 dfs 一进来就满足结算条件，返回 `[""]`。`str(cur)` 得到的是 `"['a', 'd']"`。
