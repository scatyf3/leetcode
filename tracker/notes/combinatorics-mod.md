# 组合 / 取模 速查

> 2026-11-20 整理自手写两页 + 1866 / 1569 的讨论。同内容 PDF：`combinatorics-mod.pdf`（由 `combinatorics-mod.tex` 用 xelatex 编译）。
> 展开讲的版本在 blog：[快速幂与取模](../../blog/docs/advanced/modular.md) · [组合计数](../../blog/docs/advanced/combinatorics.md)

## 0. 总览：工具链 + 三种化法

```
工具链（前一个是后一个的前置）
  快速幂 (50) ──► 取模规则 (372) ──► 逆元 y^(p-2) ──► C(n,k) mod p (2400)

应用：计数题的三种化法
  ├─ 化成公式      2929  隔板 + 容斥                不取模
  ├─ 化成 DP       1866  第一类斯特林数              取模，不用 C
  └─ 结构 + 公式   1569  递归里每层乘 C(L+R, L)       C 取模
                   1916  多叉树拓扑序 n!/∏size        阶乘 + 逆元
```

共同点：问「有多少种」，答案大，模 1e9+7；不枚举方案，直接算个数。

---

## 1. Fast pow

$x^{13} = x^8 \cdot x^4 \cdot x^1$（13 = 1101₂）。$x^1, x^2, x^4, x^8$ 每个是前一个平方 → 缓存着往上平方（via cached result），只乘指数二进制里是 1 的那几位。O(log n)。

```python
def fast_pow(base, exp, mod):
    ans = 1
    base %= mod
    while exp > 0:
        if exp & 1:                    # 这一位是 1 才乘进去
            ans = ans * base % mod
        base = base * base % mod       # x^(2^i) -> x^(2^(i+1))
        exp >>= 1
    return ans
```

Python 直接 `pow(base, exp, mod)`。

## 2. mod 规则：取模能放在哪

| | 能先取模吗 | 怎么办 |
|---|---|---|
| a) 底数 | ✓ $(a \bmod m)^k \equiv a^k$ | `base %= mod` |
| b) 乘积（加法同理） | ✓ $xy \bmod m = (x \bmod m)(y \bmod m) \bmod m$ | 每步都模 |
| c) 指数 | ✗ $a^b \not\equiv a^{b \bmod m}$ | 372：按十进制位递推；或满足条件时模 φ(m) |
| d) 除法 | ✗ $\frac{x}{y} \bmod m \ne \frac{x \bmod m}{y \bmod m}$ | 乘逆元：$\frac{x}{y} \bmod m = x \cdot y^{-1} \bmod m$ |

- 题目要的永远是**结果**取模；c) 是说「先把指数模小」这条捷径走不通。反例（m=5）：$2^5 \bmod 5 = 2$，而 $2^{5 \bmod 5} = 1$
- d) 反例（m=5）：12/4 = 3；先模得 2/4，不是整数
- **372（$a^b \bmod 1337$，b 是 base 10 的数组）**：读数字是 `x = 10x + d`，搬到指数上 $a^{10x+d} = (a^x)^{10} \cdot a^d$，每读一位 `ans = ans^10 · a^d`，马上模
- 十进制 = decimal / base 10；快速幂 = binary exponentiation

## 3. 逆元 inverse $y^{-1}$

**定义**：$y \cdot y^{-1} \equiv 1 \pmod m$，模下的「1/y」。

**求法**：m 是质数、$y \bmod m \ne 0$ 时，$y^{-1} \equiv y^{m-2} \pmod m$

**证明**：
1. 费马小定理：m 是质数、$y \bmod m \ne 0$ ⇒ $y^{m-1} \equiv 1$
2. ⇒ $y \cdot y^{m-2} \equiv 1$ ⇒ 按定义 $y^{-1} = y^{m-2}$

**费马小定理怎么来（剩余系重排法）**：$y \cdot \{1, \dots, m-1\}$ 模 m 后只是 $\{1, \dots, m-1\}$ 换了顺序。两边相乘 $y^{m-1}(m-1)! \equiv (m-1)!$，约掉 $(m-1)!$。

| m=5, y=2 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 2i mod 5 | 2 | 4 | 1 | 3 |

- 「只是重排」要两条：不出现 0、不撞车，都靠「质数整除乘积 ⇒ 整除某个因子」
- 非质数就坏：m=4, y=2 → 2, 0, 2。372 的 1337 = 7 × 191 不是质数，用不了
- 其他证法：二项式 + 归纳（$C_p^i$ 是 p 的倍数）、项链计数、拉格朗日定理

**代码**：`pow(y, MOD - 2, MOD)`，或 3.8+ 的 `pow(y, -1, MOD)`。

## 4. Combination via mod

$$C_n^k = \frac{n!}{k!\,(n-k)!}$$

select k from n regardless of order：先按顺序挑 $\frac{n!}{(n-k)!}$ 种，同一组被数了 k! 遍，除掉。$C_n^0 = C_n^n = 1$，$C_n^k = C_n^{n-k}$，k > n 为 0。

**算法：$C_n^k \bmod m$**。直接套公式要么数太大，要么有除法不能边算边模 → 三种办法：

| | 杨辉三角（comb table） | 阶乘 + 逆元（fact + inv table） | API `math.comb` |
|---|---|---|---|
| 怎么绕开除法 | 只用加法 | 除法换乘逆元 | 大整数精确算，最后 `% MOD` |
| 预处理 / 查询 | O(n²) / O(1) | O(n) / O(1) | 无 / 每次 O(k) 大整数 |
| 适用 | n ≤ 几千；模数不是质数也行 | n 到 1e5~1e6；模数必须是质数 | 只算几次、n 几千内；只有 Python |

**杨辉三角**：盯第 a 个元素，选它 / 不选它

$$C_a^b = C_{a-1}^{b-1} + C_{a-1}^{b},\qquad C_a^0 = 1$$

```python
comb = [[0] * (n + 1) for _ in range(n + 1)]
for a in range(n + 1):
    comb[a][0] = 1
    for b in range(1, a + 1):
        comb[a][b] = (comb[a-1][b-1] + comb[a-1][b]) % MOD   # 括号别漏
```

**阶乘 + 逆阶乘**：只求一次逆元，$(i-1)!^{-1} = i!^{-1} \cdot i$ 从后往前推

```python
fact = [1] * N
for i in range(1, N):
    fact[i] = fact[i - 1] * i % MOD
inv_fact = [1] * N
inv_fact[N - 1] = pow(fact[N - 1], MOD - 2, MOD)
for i in range(N - 1, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % MOD

def C(n, r):
    if r < 0 or r > n:
        return 0
    return fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD
```

## 5. Usage

| 题 | 化成什么 | 用到 |
|---|---|---|
| 50 Pow(x, n) | — | 快速幂模板 |
| 372 Super Pow | 按十进制位递推 | 快速幂 + 规则 c) |
| 2400 恰好 k 步 | $r = \frac{k+d}{2}$，答案 $C_k^r$；\|d\| > k 或 k+d 奇数为 0 | C 取模（当模板练：把 `math.comb` 换成阶乘表） |
| 2929 分糖有上限 | 隔板 $C_{n+2}^2$ + 容斥 | 不取模，k=2 直接写 |
| 1866 看得见 k 根 | 盯最矮那根：`dp[i][j] = dp[i-1][j-1] + (i-1)·dp[i-1][j]` | 取模，杨辉三角形状的 DP，不用 C |
| 1569 同一棵 BST | `ways = C(L+R, L) · ways(左) · ways(右)`，答案 −1 | C 取模（杨辉三角） |
| 1916 蚁群建房 | $\frac{n!}{\prod \text{size}(v)}$ | 阶乘 + 逆元 |

**纯模板练习**：3405（$C_{n-1}^k \cdot m \cdot (m-1)^{n-1-k}$，最推荐）· 62 / 1641（热身，不取模）· 1621 · 1735（多查询）· 2954（多重组合数）

## 6. 坑

- `a + b * c % MOD` 只模了乘积项：`%` 和 `*` 同级、比 `+` 高。1866、1569 都踩了 → 整个式子加括号
- `(ways - 1) % MOD`：ways 模完可能是 0，直接减得负数
- 1569 有序输入退化成链，递归 ~1000 层，撞 Python 默认上限 → `sys.setrecursionlimit`
- 逆元要求模数是质数；1e9+7 是，1337 不是

> 手写稿里改了的地方：
> - Fast pow 框里 `while i < n: ans *= x^i; i <<= 1` 会把 $x^1 x^2 x^4 x^8$ 全乘进去，要只乘 n 的二进制里是 1 的位（`if exp & 1`）
> - reverse → **inverse**（逆元）；$y^{-1} \equiv y^{m-2}$ 的前提「m 是质数」要写在公式旁边
> - b) 右边漏了最外层 mod m
