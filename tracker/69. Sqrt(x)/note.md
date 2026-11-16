# 69. Sqrt(x)

其实是想练习下课程学到的code实现牛顿法，但是有好多implemention的问题
1. 抽象为解`F(z)=z**2-a=0`的零点
2. 初值选a，不能选0，好像还有一些证明，只要选正，则一定能收敛
3. 还有个optional的修正fp误差，但感觉太trick了，要高精度我为啥不fp64呢，comment掉lc也不错