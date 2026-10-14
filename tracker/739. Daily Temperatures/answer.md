单调栈：栈里存还没等到更暖的 `(idx, temp)`，从底到顶温度不升；新温度严格高于栈顶就弹出并回填 `res[prev_idx] = idx - prev_idx`，弹完把自己压栈。

⚠ 结果按 `prev_idx` 回填，不能按出栈顺序 append；留在栈里的天保持 0。
