---
title: str
status: draft
order: 5
related: [/structures/string, /structures/array]
---

# str

## 一句话

**不可变的码位数组**。按下标读 O(1)；任何「修改」都是造一个新字符串。

## 底层长什么样

一块连续内存，每个字符按整串里最宽的那个字符定宽：全 ASCII 就每字符 1 字节，有中文就 2 字节，
有 emoji 就 4 字节（PEP 393）。定宽所以 `s[i]` 能直接算地址；不可变所以能当 dict 的 key。

## 复杂度

| 操作 | 复杂度 | |
|---|---|---|
| `s[i]` / `len(s)` | O(1) | |
| `s[l:r]` | O(r − l) | 拷贝 |
| `s + t` | O(len s + len t) | 造新串 |
| `''.join(parts)` | O(总长) | 先算总长一次分配 |
| `sub in s` / `s.find(sub)` | 一般很快，最坏 O(n·m) | |
| `s[::-1]` | O(n) | |

## 由此而来的坑

- **循环里 `res += ch`**：每次都可能造新串，最坏 O(n²)。CPython 有时能原地扩，但别指望；攒进 list 最后 `''.join`。
- **想改某个字符**：`s[i] = 'x'` 直接报错。先 `list(s)`，改完 `''.join`。
- **`split()` 和 `split(' ')` 不一样**：前者按任意空白切且丢掉空串，后者遇到连续空格会切出 `''`。
- **判字母数字**：`isalnum()` 对中文也是 `True`；只要 ASCII 就再加 `isascii()`。
- **字符计数**：字符集小（26 个小写字母）时用长度 26 的数组 `ord(c) - ord('a')`，比 dict 快，也能直接转 tuple 当 key。

语法卡：[tracker/syntax/str.md](https://github.com/scatyf3/leetcode/blob/main/tracker/syntax/str.md)
