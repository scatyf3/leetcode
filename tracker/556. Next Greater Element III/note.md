# 556. Next Greater Element III

换皮permutation
1. 怎么把int转list，怎么写回（有更好的解吗）
2. permutation处理重复
3. 处理int越界

### int转list

这样好些

```
digits = list(str(n))          # 1999999999 → ['1','9','9',...]
...                            # 在 digits 上跑 next permutation 三步
res = int("".join(digits))     # 拼回去
```

### int越界

py没intmax，只能写`2**31 - 1`
