# 151. Reverse Words in a String

### 怎么分词

idea是对的，但记得`s.split()`

进阶版本，基于我的这版改，处理多个空格，只要缓冲区current非空才推入word

```python
words = []
cur = []
for c in s:
    if c == " ":
        if cur:                      # 只有攒到了字符才收
            words.append("".join(cur))
            cur.clear()
    else:
        cur.append(c)
if cur:                              # 最后一个单词后面可能没有空格
    words.append("".join(cur))

```

进阶版
1. 第一个指针跳空格
2. 从第一个指针往后，收录当前非空格的词
3. 直接append i~j

```
words = []
n = len(s)
i = 0
while i < n:
    # 1. 跳过空格
    while i < n and s[i] == " ":
        i += 1
    if i == n:                       # 结尾全是空格，没有新单词了
        break
    # 2. 从 i 开始找单词结尾
    j = i
    while j < n and s[j] != " ":
        j += 1
    words.append(s[i:j])             # [i, j) 就是一个单词
    i = j                            # 从单词结尾继续

```