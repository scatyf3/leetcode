# 滑动窗口骨架:两个模板 + 两个填空位

适用题:LC 3、76、209、424、438、567 等「在数组/字符串上找满足某条件的连续区间」的题。

配套:[off-by-one-checklist.md](off-by-one-checklist.md)(索引不出错)、[two-pointer-array-partition.md](two-pointer-array-partition.md)(原地双指针)

---

## 先说「骨架」是什么

**骨架 = 一段可以复制粘贴的代码框架,里面有明确标出的填空位。** 不是函数,不是类,就是模板。

它复用的是**结构**:循环怎么转、什么时候收缩、什么时候结算。每道题只改填空位里的 1~2 行。

## 为什么是骨架,不是封装成函数/类

先看封装成类真长什么样(这份能跑,LC3 全用例过):

```python
class Window:
    def __init__(self, s):
        self.s, self.l, self.r, self.cnt = s, 0, -1, Counter()
    def extend(self):
        self.r += 1
        self.cnt[self.s[self.r]] += 1
    def shrink(self):
        self.cnt[self.s[self.l]] -= 1
        self.l += 1
    def valid(self):
        return self.cnt[self.s[self.r]] <= 1     # ← 只有这一行是题目相关的
    def __len__(self):
        return self.r - self.l + 1

w = Window(s); best = 0
for _ in range(len(s)):
    w.extend()
    while not w.valid():
        w.shrink()
    best = max(best, len(w))
```

写得挺干净,能跑。问题在于:

1. **`valid()` 是题目特定的,换题必须打开类改内部。** 抽象的价值是「写一次,之后不打开就能用」。这个类**每道题都要打开改**,那它就不是抽象,只是把 8 行摊成 30 行。
2. 想让它真通用 → `valid` 得当 callback 传进来 → callback 又要访问 `self.cnt` / `self.r` / `self.s` → 封装当场被打穿,签名变成 `Window(s, valid=lambda w: w.cnt[w.s[w.r]] <= 1)`,比 inline 难读得多。
3. 状态是可变的(`l`/`r`/`cnt` 全在变),这里又是热路径,抽象层性价比本来就低。

**骨架的诚实之处:它不假装内部不用改,它直接把「要改的地方」标出来给你填。** 结果是同样的复用(结构复用),但没有那 20 行仪式。

> 一句话:算法题的复用发生在**写代码之前**(模板 + 不变式),不是**运行时**(函数边界)。
> 工程里也一样 —— 热路径代码同样是手动内联、不封装的。不是两套价值观,是同一套价值观在不同规模下的不同结论。

---

## 骨架 A:求**最长**合法窗口

不变式:**结算时窗口一定合法**。所以先收缩到合法,再结算。

```python
state = init()
l = 0
best = 0
for r, x in enumerate(arr):
    add(state, x)                    # ① 纳入 r
    while not valid(state):          # ② 不合法就收缩(注意是 while 不是 if)
        remove(state, arr[l]); l += 1
    best = max(best, r - l + 1)      # ③ 结算(此刻必合法)
return best
```

## 骨架 B:求**最短**合法窗口

不变式:**合法时才结算,结算完立刻收缩试试更短的**。结算在 while 内部。

```python
state = init()
l = 0
best = INF
for r, x in enumerate(arr):
    add(state, x)                    # ① 纳入 r
    while valid(state):              # ② 合法就一直缩
        best = min(best, r - l + 1)  # ③ 先结算
        remove(state, arr[l]); l += 1
return 0 if best == INF else best
```

**A 和 B 的差别只有两处**:`while` 条件取反、结算在循环外/内。选哪个看题目求最长还是最短。

---

## 填空位对照表(全部验证跑过)

| 题 | 骨架 | `state` | 收缩条件 |
|----|------|---------|----------|
| **3** 无重复最长子串 | A | `Counter` | `cnt[x] > 1` |
| **424** 替换 k 次后最长同字符 | A | `Counter` + `mx`(历史最大频次) | `(r-l+1) - mx > k` |
| **209** 和 ≥ target 最短子数组 | B | `sum` | `tot >= target` |
| **76** 最小覆盖子串 | B | `Counter(t)` + `miss` | `miss == 0` |
| **438/567** 找异位词 | 定长窗口 | `Counter` | `r-l+1 > len(p)` |

### LC 3

```python
cnt = Counter(); l = 0; best = 0
for r, x in enumerate(s):
    cnt[x] += 1
    while cnt[x] > 1:
        cnt[s[l]] -= 1; l += 1
    best = max(best, r - l + 1)
return best
```

### LC 424

```python
cnt = Counter(); l = 0; best = 0; mx = 0
for r, x in enumerate(s):
    cnt[x] += 1; mx = max(mx, cnt[x])
    while (r - l + 1) - mx > k:          # 窗口内非众数的个数 > k 就不合法
        cnt[s[l]] -= 1; l += 1
    best = max(best, r - l + 1)
return best
```

### LC 209

```python
tot = 0; l = 0; best = float('inf')
for r, x in enumerate(nums):
    tot += x
    while tot >= target:
        best = min(best, r - l + 1)
        tot -= nums[l]; l += 1
return 0 if best == float('inf') else best
```

### LC 76

```python
need = Counter(t); miss = len(t); l = 0; bl, br = 0, -1
for r, x in enumerate(s):
    if need[x] > 0: miss -= 1
    need[x] -= 1
    while miss == 0:
        if br == -1 or r - l < br - bl: bl, br = l, r
        need[s[l]] += 1
        if need[s[l]] > 0: miss += 1
        l += 1
return s[bl:br+1] if br != -1 else ""
```

---

## 骨架版 vs 官方「特化版」

LC 3 的官方解不是骨架版,而是**特化**:

```python
last = {}; l = 0; best = 0
for r, c in enumerate(s):
    if c in last and last[c] >= l:
        l = last[c] + 1          # 一步跳到位, 把 while 收缩塌成一次跳跃
    last[c] = r
    best = max(best, r - l + 1)
return best
```

对比:

| | 骨架版 | 特化版 |
|---|---|---|
| 复杂度 | O(n),最坏 2n 步 | O(n),n 步 |
| 通用性 | 一套解 6 道题 | 只解这一道 |
| 下标算术 | 只有 `l += 1` | 有 `last[c] + 1` ← **off-by-one 高发区** |
| `>= l` 守卫 | 不需要 | 必须有,漏了就错 |

**默认写骨架版。**它显示你识别出了题型而不是背了一道题;而且它天生绕开了 `last[c] + 1` 和 `>= l` 这两个坑(参见 [off-by-one-checklist.md](off-by-one-checklist.md) 的实战复盘)。特化版留作「被问到能不能更快」时的加分项。

---

## 拿到新题的 3 个问题

1. 求**最长**还是**最短**? → 选骨架 A 还是 B
2. 窗口里要维护**什么统计量**? → `state`
3. **什么时候算不合法**? → 收缩条件

回答完这三句,代码就是填空。真正要练的是把这三句说出来的速度,不是把代码写短。

## 两个易错点

- ② 处是 `while` 不是 `if`。一次收缩未必够(LC 209 里可能连缩好几格)。
- 骨架 A 的结算必须在 while **之后**,骨架 B 的结算必须在 while **之内**。写反了就是在非法窗口上结算 / 漏掉最短解。
