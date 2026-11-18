---
title: 快速幂与取模
status: draft
order: 1
alias: []
related: [/paradigms/bit-manipulation, /paradigms/recursion]
---

# 快速幂与取模

> 取模下哪些运算能随手做、除法为什么不行；快速幂为什么是 $O(\log n)$；逆元怎么用快速幂求

## 一句话

答案要对 1e9+7 取模时，加、减、乘随时取模，除法要换成乘逆元；指数大到 10⁹ 以上，用快速幂：
把指数拆成二进制，$x^{13} = x^8 \cdot x^4 \cdot x^1$，只要乘 $\log n$ 次。

## 怎么认出这类题

题目说「返回结果对 10⁹ + 7 取模」；或者幂次、指数本身非常大。

建在 L3 的：[位运算](../paradigms/bit-manipulation)（迭代版按二进制位走）· [递归](../paradigms/recursion)（分治版每层规模减半）

## 题单

加粗的是代表题。

| 题 | 练什么 |
|---|---|
| [50. Pow(x, n)](https://leetcode.com/problems/powx-n/) | 前置题，不在 ACM 单里：快速幂模板 + 负指数 |
| **[372. Super Pow](https://leetcode.com/problems/super-pow/)** | 快速幂，指数很大时取模 |

## 原理

### 1. 取模下能做什么

记 $a \bmod p$ 为 $a$ 除以 $p$ 的余数。加、减、乘都可以**先取模再算**，结果不变：

$$
(a + b) \bmod p = \big((a \bmod p) + (b \bmod p)\big) \bmod p
$$

$$
(a \cdot b) \bmod p = \big((a \bmod p) \cdot (b \bmod p)\big) \bmod p
$$

**为什么成立**：把 $a$ 写成 $a = q_a p + r_a$，$b = q_b p + r_b$，乘开：

$$
a \cdot b = (q_a q_b p + q_a r_b + q_b r_a)\, p + r_a r_b
$$

前面那一大坨是 $p$ 的倍数，取模时全部消掉，只剩 $r_a r_b$。加法同理。

所以计数题里每一步加完、乘完都可以立刻 `% MOD`，数永远不会超过 $p^2$。

**减法**：$(a - b) \bmod p$ 在 C++ / Java 里可能是负数，要写成 `(a - b + MOD) % MOD`。Python 的 `%` 结果永远非负，不用加。

**除法不行**：$6 / 2 = 3$，但先对 4 取模，$6 \bmod 4 = 2$，$2 / 2 = 1 \ne 3$。
除法要换成「乘逆元」，见第 3 节。

**为什么模数常是 $10^9 + 7$**：它是质数（第 3 节求逆元要用）；小于 $2^{30}$，两个余数相乘小于 $2^{60}$，C++ 的 `long long` 装得下。

### 2. 快速幂

**直觉**：$x^{13}$ 老老实实乘要 12 次。可是 $13 = 8 + 4 + 1$，所以

$$
x^{13} = x^{8} \cdot x^{4} \cdot x^{1}
$$

而 $x^1, x^2, x^4, x^8$ 每个都是前一个的平方，一路平方上去只要 3 次。**指数这一层的加法，到了值这一层变成乘法。**

**一般地**，把 $n$ 写成二进制 $n = \sum_i c_i 2^i$（$c_i \in \{0, 1\}$）：

$$
x^n = \prod_{i:\, c_i = 1} x^{2^i}
$$

从低位往高位扫 $n$ 的每一位，维护两个量：

- `base`：当前这一位对应的 $x^{2^i}$，每走一位平方一次
- `ans`：已经扫过的、是 1 的那些位乘起来

**正确性（循环不变量）**：记原来的底数和指数为 $X, N$。每一轮开始时都有

$$
\text{ans} \cdot \text{base}^{\,\text{exp}} = X^{N}
$$

- 开始：$\text{ans} = 1$，$\text{base} = X$，$\text{exp} = N$，成立。
- 一轮里：若 exp 是奇数，$\text{base}^{\text{exp}} = \text{base} \cdot \text{base}^{\text{exp}-1}$，把那个 base 乘进 ans；
  剩下的 $\text{exp}-1$ 是偶数，$\text{base}^{\text{exp}-1} = (\text{base}^2)^{(\text{exp}-1)/2}$，
  所以 base 平方、exp 右移一位。乘积不变。
- 结束：$\text{exp} = 0$，$\text{base}^0 = 1$，所以 $\text{ans} = X^N$。$\blacksquare$

exp 每轮右移一位，一共 $\lfloor \log_2 N \rfloor + 1$ 轮，**复杂度 $O(\log N)$**。

**手推 $3^{13}$**（$13 = 1101_2$，从低位读）：

| exp | 二进制 | 最低位 | base | ans |
|---|---|---|---|---|
| 13 | 1101 | 1 → 乘进去 | $3$ | $3$ |
| 6 | 110 | 0 → 跳过 | $3^2 = 9$ | $3$ |
| 3 | 11 | 1 → 乘进去 | $3^4 = 81$ | $3 \cdot 81 = 243$ |
| 1 | 1 | 1 → 乘进去 | $3^8 = 6561$ | $243 \cdot 6561 = 1594323 = 3^{13}$ |

### 3. 逆元：取模下的除法

**定义**：$a$ 在模 $p$ 下的逆元 $a^{-1}$，是满足 $a \cdot a^{-1} \equiv 1 \pmod p$ 的数。
有了它，「除以 $a$」就换成「乘 $a^{-1}$」：

$$
\frac{b}{a} \bmod p = b \cdot a^{-1} \bmod p
$$

例：模 7 下 $3^{-1} = 5$，因为 $3 \cdot 5 = 15 = 2 \cdot 7 + 1$。验证 $6 / 3 = 2$：$6 \cdot 5 = 30$，$30 \bmod 7 = 2$。✓

**怎么求：费马小定理**。$p$ 是质数、$a$ 不是 $p$ 的倍数时：

$$
a^{p-1} \equiv 1 \pmod p
\quad\Longrightarrow\quad
a \cdot a^{p-2} \equiv 1 \pmod p
\quad\Longrightarrow\quad
a^{-1} = a^{p-2} \bmod p
$$

$p - 2 \approx 10^9$，这一步就是快速幂。**快速幂 → 逆元 → 组合数**，这条链在 [组合计数](./combinatorics) 里接着用。

::: details 费马小定理为什么成立（选看）
把 $1, 2, \dots, p-1$ 每个都乘上 $a$ 再模 $p$：$a, 2a, \dots, (p-1)a$。

这 $p-1$ 个数两两不同：若 $ia \equiv ja$，则 $p \mid (i - j) a$。$p$ 是质数且不整除 $a$，只能 $p \mid (i - j)$，而 $|i - j| < p$，所以 $i = j$。
它们又都不是 0，所以正好是 $1, \dots, p-1$ 换了个顺序。两组数各自乘起来相等：

$$
a^{p-1} \cdot (p-1)! \equiv (p-1)! \pmod p
$$

$(p-1)!$ 和 $p$ 互质，两边约掉，得 $a^{p-1} \equiv 1$。$\blacksquare$
:::

### 4. 指数大到存不下：按十进制位递推（372）

372 的指数 $b$ 以数组形式给出，最多 2000 位。做法和平时「把一串数字读成整数」一样：

```python
num = 0
for digit in b:
    num = num * 10 + digit      # [1, 2, 3]: 0 → 1 → 12 → 123
```

指数存不下，就不存 `num`，只存 $a^{\text{num}}$。设 $b$ 有 $n$ 位，$b[i]$ 是从高位数第 $i$ 位（下标从 0 开始），定义

$$
f(i) = a^{\,\overline{b[0]\,b[1]\cdots b[i-1]}} \bmod 1337
$$

即 $a$ 的「$b$ 的前 $i$ 位组成的十进制数」次方。读入下一位 $b[i]$，指数从 $\text{num}$ 变成 $10 \cdot \text{num} + b[i]$：

$$
f(0) = 1, \qquad f(i+1) = f(i)^{10} \cdot a^{b[i]} \bmod 1337, \qquad \text{答案} = f(n)
$$

| 对指数 num 做的 | 对 $f = a^{\text{num}}$ 做的 | 用到的幂运算律 |
|---|---|---|
| `num * 10` | `f ** 10` | $(a^x)^{10} = a^{10x}$ |
| `+ digit` | `* a ** digit` | $a^x \cdot a^y = a^{x+y}$ |

## 模板

::: code-group

```python [快速幂（取模）]
def fast_pow(base, exp, mod):
    """base^exp % mod, exp >= 0。和 50 的写法一样, 只是每次乘完都取模。"""
    ans = 1
    base %= mod                         # 先缩小, base 可能很大
    while exp > 0:
        if exp & 1:                     # 这一位是 1: 把当前的 x^(2^i) 乘进答案
            ans = ans * base % mod
        base = base * base % mod        # x^(2^i) -> x^(2^(i+1))
        exp >>= 1
    return ans
```

```python [逆元]
MOD = 10**9 + 7                         # 必须是质数

def inv(a):
    """a 在模 MOD 下的逆元。费马小定理: a^(p-2)。a 不能是 MOD 的倍数。"""
    return fast_pow(a, MOD - 2, MOD)

# Python 3.8+ 也可以直接写 pow(a, -1, MOD)
# 内置三参数 pow(base, exp, mod) 本身就是快速幂, 比赛和 LC 里直接用它
```

```python [矩阵快速幂]
def mat_mul(A, B, mod):
    rows, inner, cols = len(A), len(B), len(B[0])
    C = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for t in range(inner):
            if A[i][t]:
                for j in range(cols):
                    C[i][j] = (C[i][j] + A[i][t] * B[t][j]) % mod
    return C

def mat_pow(M, exp, mod):
    """骨架和 fast_pow 一模一样: 1 换成单位矩阵, 乘法换成矩阵乘法。"""
    size = len(M)
    ans = [[int(i == j) for j in range(size)] for i in range(size)]
    while exp > 0:
        if exp & 1:
            ans = mat_mul(ans, M, mod)
        M = mat_mul(M, M, mod)
        exp >>= 1
    return ans

def fib(n, mod=10**9 + 7):
    """[F(n), F(n-1)] = [[1,1],[1,0]]^(n-1) · [F(1), F(0)]。n 到 10^18 也只要 60 轮。"""
    if n == 0:
        return 0
    return mat_pow([[1, 1], [1, 0]], n - 1, mod)[0][0]
```

```python [验证]
import random

for _ in range(2000):
    b, e, m = random.randrange(10**12), random.randrange(10**6), random.randrange(1, 10**9)
    assert fast_pow(b, e, m) == pow(b, e, m)

for a in range(1, 2000):
    assert a * inv(a) % MOD == 1

f = [0, 1]
for i in range(2, 300):
    f.append(f[-1] + f[-2])
assert all(fib(n) == f[n] % MOD for n in range(300))
```

:::

**矩阵快速幂什么时候用**：线性递推（斐波那契、[790](./profile-dp) 那种铺砖转移）要算到第 $10^{18}$ 项。
把一步转移写成矩阵 $M$，第 $n$ 项就是 $M^n$ 乘初值，$O(k^3 \log n)$，$k$ 是状态数。

## 例子

### 50. Pow(x, n)：模板 + 负指数

自己的 [sol.py](https://github.com/scatyf3/leetcode/blob/main/tracker/50.%20Pow%28x%2C%20n%29/sol.py)，不取模、浮点版：

```python
class Solution:
    def myPow(self, x: float, n: int) -> float:
        ans = 1
        negative = False
        if n < 0:
            n = -n
            negative = True
        while n > 0:
            if n & 1:
                ans *= x
            x *= x
            n = n >> 1
        if negative:        # 不用 1/x 而是 1/ans，减少 fp 误差
            ans = 1 / ans
        return ans
```

- **负指数**：$x^{-n} = 1 / x^n$，先按正的算，最后取倒数。只做一次除法，误差也只引入一次。
- C++ / Java 里 `n = -n` 会溢出：$n = -2^{31}$ 取反超出 int。要先转 `long long`。Python 没这个问题。

### 372. Super Pow：按十进制位递推

$a^b \bmod 1337$，$b$ 是最多 2000 位的数组。按原理第 4 节的 $f(i)$ 递推：

```python
class Solution:
    def superPow(self, a: int, b: list[int]) -> int:
        MOD = 1337
        a %= MOD                      # a 最大约 2^31, 先缩小

        ans = 1                       # ans = f(i) = a^(已经读过的那段数) mod 1337
        for digit in b:               # 从高位往低位读
            shifted = pow(ans, 10, MOD)       # 指数 × 10
            extra = pow(a, digit, MOD)        # 指数 + digit
            ans = shifted * extra % MOD
        return ans
```

手推 $a = 2$，$b = [1, 2, 3]$：

| 读到 | 已读的数 | ans |
|---|---|---|
| 开始 | 0 | $1$ |
| 1 | 1 | $1^{10} \cdot 2^1 = 2$ |
| 2 | 12 | $2^{10} \cdot 2^2 \bmod 1337 = 85 = 2^{12} \bmod 1337$ |
| 3 | 123 | $85^{10} \cdot 2^3 \bmod 1337 = 1191 = 2^{123} \bmod 1337$ |

**复杂度**：$b$ 有 $n$ 位，每位两次指数不超过 10 的 `pow`，$O(n)$。

**能不能一行**：`pow(a, int(''.join(map(str, b))), 1337)` 在 Python 里能过，整数没上限。
但这题考的就是「指数存不下怎么办」，面试里这么写等于没答。

## 栽过的坑

- **372 第一版：每读一位就乘一次 $a$**。`for d in b: ans *= a`，算出来是 $a^{\text{位数}}$，不是 $a^b$。$b = [1, 0]$ 时应该是 $a^{10}$，它给 $a^2$。
  位与位之间是「指数 × 10 再加」，不是一位一个 $a$。
- **372 笔记里把两层混了**：写成「ans × 10，再加上 $a^d$」。乘 10 和加 $d$ 都是对**指数**做的；
  落到值 $a^{\text{num}}$ 上，乘变成乘方，加变成相乘：ans 先 `** 10`，再 `* a ** d`。

## 面试追问

::: details Q：快速幂迭代版和递归版有什么区别？
递归版：$x^n = (x^{n/2})^2$，$n$ 是奇数再多乘一个 $x$。从高位往低位，代码短，但有 $O(\log n)$ 的栈。
迭代版（上面的模板）：从低位往高位，$O(1)$ 额外空间。两者乘法次数一样。
:::

::: details Q：372 能不能先把指数对 1140 取模（欧拉定理）？
$\varphi(1337) = \varphi(7 \cdot 191) = 6 \cdot 190 = 1140$，欧拉定理说 $\gcd(a, 1337) = 1$ 时 $a^{1140} \equiv 1$，指数可以模 1140。

但 $a$ 可能是 7 或 191 的倍数，这时不成立。反例：$a = 7$，$b = 1140$，正确答案 $7^{1140} \bmod 1337 = 574$，直接模掉变成 $7^0 = 1$。
要用得写扩展欧拉定理（指数模 $\varphi$ 之后再加回一个 $\varphi$）。按十进制位递推不需要任何前提，更稳。
:::

::: details Q：模数不是质数时怎么求逆元？
费马小定理要求 $p$ 是质数。一般情况用扩展欧几里得解 $ax + py = 1$，$x$ 就是逆元；$\gcd(a, p) \ne 1$ 时逆元不存在。
Python 的 `pow(a, -1, m)` 内部就是这么做的，不存在时抛 `ValueError`。
:::

::: details Q：为什么乘完要立刻取模，不能最后一起模？
C++ / Java 里两个 $10^9$ 级别的数乘一次就到 $10^{18}$，再乘就溢出。
Python 不溢出，但大整数越来越长，乘法越来越慢：372 里攒到最后再模，中间的数有上千位。
:::
