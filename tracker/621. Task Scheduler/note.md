# 621. Task Scheduler

1. 这个就是个非常system的题，从例子得知有两个可能的bound 1. lauch task太多 2. 最长路径
2. 但我没考虑如何计算最长路径的tail，几条同样长的最长路径影响tail需要多少interval
3. 省🧠的解是heap模拟。 
  1. 一个heap存可以被lauch的task，order by cnt，cnt多的先启动 
  2. deque存等cd的task