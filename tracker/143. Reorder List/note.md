# 143. Reorder List

我觉得这是很经典的题:

1. 快慢指针找中间,slow 是奇数的正中间、偶数的中间之前(左中点)
2. reverse,记得 while 的论据是 `curr is not None`
3. merge 2

> 这三块零件已抽成模板:[notes/linked-list-template.md](../notes/linked-list-template.md)
> [sol.py](sol.py) = 原始解法 + 复盘注释;[sol2.py](sol2.py) = 消掉全部特判的精简版。
