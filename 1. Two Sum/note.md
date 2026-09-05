# 1. Two Sum

一个remain - index的hash
1. 用hash map
2. 怎么构建hash map，用剩下的半段，有点像双括号的右括号 - 左括号映射
3. 怎么用还是有小坑，这里的契约是「存target-nums[i]」，查后续迭代的nums[i]（而不是remain）