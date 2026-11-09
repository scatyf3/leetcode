# Python 循环控制语法坑

读法和 [str.md](str.md) 一样：**从头通读**当 checklist，或者在看板里 `🧠 复习 → 语法` 按 FSRS 抽卡。
格式约定见 [dashboard/syntax.py](../dashboard/syntax.py)。

收录标准同样是**只收自己真栽过的**。

---

## 一轮 for 里「一个都没放成」就退出外层 while，怎么写最省事

```python
while True:
    for ch in candidates:
        if not ok(ch):
            continue
        res.append(ch)
        break
    if [这一轮 res 没变]:
        return res
```

---

```python
while True:
    for ch in candidates:
        if not ok(ch):
            continue
        res.append(ch)
        break
    else:                  # 和 for 对齐，不和 if 对齐
        return res
```

`for ... else`：**for 没被 `break` 就正常跑完**时才执行 `else`。
这里只有放成功才 `break`，所以「没 break」=「一个都没放成」，正好是退出条件。

不想用 `for-else` 也行，按原话写：

```python
before = len(res)
for ...:
    ...
if len(res) == before:
    return res
```

两种写法等价，**挑一种固定下来**。别回到「手动列出放不了的所有情况」—— 那就是分类讨论。

栽过：1405

## 几个 `if 条件: continue` 叠在一起，等价于什么

```python
for ch in ...:
    if A:
        continue
    if B:
        continue
    do_something()
    break
```

---

等价于把后面的代码包进**条件取反再 and**：

```python
for ch in ...:
    if not A and not B:        # 德摩根：= if not (A or B)
        do_something()
        break
```

`continue` = 跳过本轮剩下的代码，直接进下一轮。这种「先把不要的排除掉」的写法叫 **guard clause（卫语句）**：
每个排除条件一行、能各配注释、主逻辑少缩一层。条件多时比合并版好读。

两个坑：

- **嵌套循环**：`continue` 只管**最内层**循环，写在内层 for 里跳不到外层下一轮
- **`while` 里手动更新变量**：

  ```python
  i = 0
  while i < n:
      if bad(i):
          continue      # 跳过了下面的 i += 1 → 死循环
      i += 1
  ```

  `for` 自动取下一个元素，没这个问题。

栽过：1405
