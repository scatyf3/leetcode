<!-- chat df5f19da/c35b75e3 2026-11-22 -->

#### 🧑 我

```python
class Solution:
    def totalFruit(self, fruits: list[int]) -> int:
        # cnt => top2
        cnt = Counter()
        # 枚举r，根据cnt状态收缩l
        l=0
        r=0
        res=0
        while r<len(fruits):
            cnt[fruits[r]]+=1
            if len(cnt)>2:
                print("trigger eviction")
                print(cnt)
                print(fruits[l:r+1])
                # evict min cnt instead of prev, 如果counter一样，优先考虑时序
                to_evict = min(cnt.values()) 
                while cnt[to_evict]>0 and l<=r :
                    if fruits[l]==to_evict:
                        cnt[to_evict]-=1
                    l+=1
                    #print(l)
                    #print(cnt)
                del cnt[to_evict]
            # valid
            res=max(res,r-l+1)
            r+=1
        return res
```


        

我注释的这个意思怎么更好实现

#### 🤖 Claude

先别实现，**「淘汰数量最少的」这个想法本身不对**。反例 `[1,1,2,3,3,3]`，r 走到第一个 3 时：

```
1 1 2 3      cnt = {1:2, 2:1, 3:1}
```

| 淘汰谁 | l 移到 | 之后最长窗口 |
|---|---|---|
| 2（数量最少，时序更早） | 下标 3，两个 1 也一起没了 | `[3,3,3]` = 3 |
| 1 | 下标 2 | `[2,3,3,3]` = **4** ✓ |

原因是 **l 只能从左往右走，你没法点名淘汰谁**。要删掉 2，就得先路过前面所有的 1。所以不用看数量，你注释里的「时序」才是对的那一半。

**提示**：也不用提前算出 `to_evict`。l 一步步往右，**谁先减到 0，就是谁被淘汰**：

```python
while ______:          # 窗口还不合法
    x = fruits[l]
    ______             # x 离开窗口
    if ______:         # x 没了
        ______
    l += 1
```

四个空，填完就能替换你整个 `if` 块，外层不用动。

你现在的代码里还有两个 bug，这样写就都没了：
- **`min(cnt.values())` 返回的是次数，不是水果种类。** 想拿种类要写 `min(cnt, key=cnt.get)`。Example 2 就会因此返回 2，正确答案是 3。
- **l 路过其他水果时没有减它们的 cnt。** 窗口里已经没有 1 了，cnt 里却还留着。

填完发我看看。

#### 🧑 我

那怎么evict呢

#### 🤖 Claude

evict 就是**从左边一个一个往外扔，扔到只剩 2 种为止**。不用选谁走。

还是 `[1,1,2,3]`，cnt = `{1:2, 2:1, 3:1}`，3 种，超了：

| 步骤 | 扔掉 | cnt | 几种 |
|---|---|---|---|
| l = 0 | 1 | `{1:1, 2:1, 3:1}` | 3，继续 |
| l = 1 | 1 | `{1:0, 2:1, 3:1}` → 删掉 key 1 | 2，停 |

l 停在下标 2，窗口是 `[2,3]`。1 就这样自然被淘汰了。

每扔一个，做三件事：

```python
x = fruits[l]
cnt[x] -= 1          # 1. 扔掉一个
if cnt[x] == 0:      # 2. 扔完了就删 key
    del cnt[x]
l += 1               # 3. 左边界右移
```

第 2 步必须有：`len(cnt)` 数的是 key 的个数，`{1:0, 2:1, 3:1}` 的 len 还是 3，不删就会一直扔下去。

剩最后一个空给你：这四行外面套一个 `while`，**条件是什么？** 看表格最后一列，什么时候「继续」，什么时候「停」。
