主栈旁边同步一个 `minstk`，存「到这一层为止的最小值」：push 压 `min(minstk[-1], val)`，pop 两栈一起弹，`getMin` 读 `minstk[-1]`。

⚠ 空栈时没有 `minstk[-1]` 可比，直接压 `val`。
