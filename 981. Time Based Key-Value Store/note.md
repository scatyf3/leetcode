# 981. Time Based Key-Value Store

怎么存，一个key，对应t,value的list pairt，这里相比于我们的方案，`{key:{timestamp:value}}` 的好处是t和val有序

然后get的时候做binary search搜缝，recall binary search结束的时候，l和r分别停在

```
下标:   0    1    2    3    4
P:      T    T    T    F    F
                  ↑    ↑
                  r    l        退出时必然 l == r + 1
```

这里timestamp向前维护，返回r有道理

还有个区别是我们没有if-elif-else三分支，即判断搜中，搜缝可以不判断命中吗？
1. 对，第一个分支cover了命中
2. 有重复元素时，三分支的 == 就 return 是有害的。a = [1,2,2,2,5]，求「最后一个 ≤ 2」：
  1. 三分支：mid=2，a[2]==2，立刻 return 2 —— 但答案是下标 3。它返回的是随便某一个匹配位置，取决于二分路径。
  2. 搜缝 P = a[i] <= 2：T T T T F → r = 3 