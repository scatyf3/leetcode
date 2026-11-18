# 50. Pow(x, n)

迭代`x*=x`，然后`n=n>>1`，然后如果n&1则把当前的x乘到answer里