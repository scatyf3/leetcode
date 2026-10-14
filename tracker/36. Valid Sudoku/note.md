# 36. Valid Sudoku

1. do we need to actually solve this?
2. naive way to solve is add constrain by iterate through row/col/grid, check constrain are conflict or not, but handwritten is complex...
agent：把循环翻过来——不再是「对每个组，收集它的格子」，而是「对每个格子，算出它属于哪些组」

说起来我有个问题，哪里说了input只能保证valid和invalid，就没有「不确定」这个状态吗。
不过好像也不一样，valid=能解+不确定

b的indexing怎么想，这里的cot是
```python
# b = ?
# 定义box 012/345/678
# for x or y 012 - 0, 345 - 1, 678-2
# 012 - 0, 345 - 3, 678-6
# 只要indexing consist 映射到全部就行，甚至不用管行和列
b = (r // 3) * 3 + c // 3 
```