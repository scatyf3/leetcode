---
title: 位运算
status: draft
order: 20
alias: []
related: [/structures/bit, /paradigms/1d-dp]
---

# 位运算

我在 plan 里给这组的评语是「知道就秒、不知道就卡，学不到可迁移的东西」。所以这页不讲大道理，
只收几个**要记住的恒等式**，每个配一道题，各自为什么成立画一下。int 当位数组本身（读写第 i 位、位宽、负数）见 [二进制位](../structures/bit.md)。

## n & (n-1)：消掉最低位的那个 1（191）

```
n       = ...a 1 0000     最低位的 1 后面跟着 k 个 0
n-1     = ...a 0 1111     借位：那个 1 变 0，后面的 0 全变 1
n&(n-1) = ...a 0 0000     高位不变，最低位的 1 没了
```

```python
def hammingWeight(self, n: int) -> int:      # LC 191
    counter = 0
    while n:
        n &= n - 1
        counter += 1
    return counter
```

循环次数就是 1 的个数，不是 32。顺带：`n > 0 and n & (n - 1) == 0` 就是「n 是 2 的幂」（只有一个 1）。

## n & -n：只留最低位的那个 1

`-n` 是 `~n + 1`：取反之后最低位那个 1 以下全变成 1，`+1` 一路进位又把它们变回 0、把那一位变回 1，上面的位保持取反：

```
n    = ...a 1 0000
~n   = ...ā 0 1111
-n   = ...ā 1 0000
n&-n = 0..0 1 0000
```

`(n & -n).bit_length() - 1` 就是末尾有几个 0。338 的 Solution5 用它把「模拟 +1 进位」压成一行。

## 异或抵消：a ^ a = 0，a ^ 0 = a

异或满足交换律，成对出现的全部抵消，剩下的就是落单的那个。136 Single Number 我用的是 set 开关
（没见过就 `add`，见过就 `remove`）；把所有数异或起来是同一个「成对抵消」，只是空间 O(1)。

## 固定位宽逐位搬运（190）

```python
def reverseBits(self, n: int) -> int:        # LC 190
    res = 0
    for _ in range(32):              # 固定 32 轮，不能写 while n:
        res = (res << 1) | (n & 1)   # res 左移腾出一格，填入 n 的最低位
        n >>= 1                      # n 丢掉刚用过的最低位
    return res
```

和 191 放一起看循环条件：190 要处理每一位，前导零也要搬，所以固定 32 轮；191 只数 1，n 归零就是数完了，`while n` 才对。
**零位算不算数，决定循环写 `for` 还是 `while`。**

## 按位 DP（338）

`i >> 1` 是 `i` 去掉最低位，比 `i` 小，已经算过了：

```python
def countBits(self, n: int) -> List[int]:     # LC 338
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

`dp[i] = dp[i & (i - 1)] + 1` 也行（去掉最低位的 1，少一个 1）。338 我一开始想的是「模拟进位 O(n log n)，再找一个闭式公式」，
漏了中间那一级：暴力 → **复用已算过的答案** → 闭式公式。公式其实存在，但它是 O(n log n)，「有公式」和「能省时间」是两件事
（[338 的 note](https://github.com/scatyf3/leetcode/blob/main/tracker/338.%20Counting%20Bits/note.md)）。
