# 438. Find All Anagrams in a String

这玩意不熟悉啊

1. 依旧骨架，枚举右，收缩左
2. 左闭右闭区间，这和用for循环枚举右有关，就是个protocol
3. 先append 现在的r再收缩左
4. 收缩左的时候，先从cnt remove l，然后再l+=1

然后看性质了，这里是必须窗口长度exact match，有时候窗口长度大于等于也valid，每收缩一步就要记录一步