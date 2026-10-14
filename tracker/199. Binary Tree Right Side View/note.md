# 199. Binary Tree Right Side View

还是bfs，还是deque，而不是stack，然后update了一版sol

这里用deque还是stack的本质区别是啥？
tldr： deque有稳定左右顺序，stack是交替
```
frontier 容器	层内顺序	天然适配
deque (FIFO)	稳定 L→R	102 / 199 / 515 / 637
stack，固定 push 序	逐层复合置乱	没用，纯 bug
stack，交替 push 序	L→R / R→L 交替	103 锯齿
```