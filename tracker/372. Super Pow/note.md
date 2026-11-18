# 372. Super Pow

1. fastpow算法不变
2. 核心思路是按十进制迭代，每迭代一步指数 x 10 再加上本步的 d，落到 ans 上就是 ans 先 ^10，再乘本步的 $a^d$

设 b 有 n 位，b[i] 是从高位数第 i 位（下标从 0 开始），定义

$$f(i) = a^{\,\overline{b[0]\,b[1]\cdots b[i-1]}} \bmod 1337$$

即 a 的「b 的前 i 位组成的十进制数」次方。

$$f(0) = 1,\qquad f(i+1) = f(i)^{10} \times a^{b[i]} \bmod 1337,\qquad \text{答案} = f(n)$$
