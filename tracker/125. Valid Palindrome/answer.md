左右指针往中间走，边走边跳过非字母数字，比 `s[l].lower() != s[r].lower()`。

语法细节：
- 判「字母或数字」用 `c.isalnum()`，**不是** `isalpha()`（会漏数字，`"0P"` 判成 True）
- `lower()` 在比较时对单个字符调，别先 `s = s.lower()` 造一整串
- 内层跳过的 while 要带 `l < r` 守卫：`while l < r and not s[l].isalnum(): l += 1`，否则全是标点时越界

详见语法卡 [str.md](../syntax/str.md)。
