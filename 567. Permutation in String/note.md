# 567. Permutation in String

 
sol4是我想的counter版，用s1 init一个need，但是next step和agent的不一样
1. 我想的是滑窗扣need里的计数，如果滑窗里的char在need里就+-，如果counter为空或者都是0 则valid。
    1. 如果用全0判，繁琐
    2. 如果以为空为判断，remove很烦，也不知道咋写
2. agent：滑窗init和更新s2 的counter，直接判相等
    1. python会忽略value=0的key，which 也是py的语义


这里输在语法不熟悉。。。