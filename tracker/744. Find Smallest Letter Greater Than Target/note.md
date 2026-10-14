# 744. Find Smallest Letter Greater Than Target

说起来为啥第一个if对应map里的true，这里的道理在哪里。

T 只是「if 里写的条件成立」的意思，写 < 还是 > 由你决定。有序数组配上单调条件，整个数组一定分成两块，只有两种形状：

```
T T T F F F      条件是 < 或 <=   （34 的第一个二分、35）
F F F T T T      条件是 > 或 >=   （744）
```

或者写成l和r