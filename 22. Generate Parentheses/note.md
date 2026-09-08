# 22. Generate Parentheses

## 思路

1. 回溯
2. 这东西能用stack解吗
    1. left remain和right remain就是压扁的stack
    2. 可以递归改遍历但是没必要

## framwork

之前有个naive的写法，但这不对

```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        cur_state=[]
        res = dfs(cur_state,n,n)
        res_str = []
        for sub_lst in res:
            res_str.append("".join(sub_lst))

    def dfs(cur_state,left_remain,right_remain):
        if left_remain==0:
            for _ in range(right_remain):
                cur_state.append(")")
            return cur_state
        
        for i in range(1,left_remain+1):
            cur_state.append("(")
            res.append(dfs(cur_state,left_remain-i,right_remain))
            for j in range(1,right_remain+1):
                cur_state.append(")")
                res.append((dfs(cur_state,left_remain-i,right_remain-j))

        return res
```

和正确的solution的区别是
1. 正确sol一次只决定一个括号，其他递归
2. 然而我们试图枚举全部，这里有点写成bfs了嘛？

我那个可以写，一步决策粒度是放多少左和右，但是这里有重复，不如每步决定一个左括号和一个右括号

## 细节

啥时候在dfs中修改，啥时候返回结果？回溯一定要dfs中修改吗？

| | 路径怎么传 | 要撤销吗 | 代价 |
|---|---|---|---|
| **A 共享可变** | 一份 `path`，全程复用 | **要**，`append`/`pop` 成对 | 内存 O(深度)；收集时**必须拷贝** `path[:]` |
| **B 传不可变值** | `dfs(path + [x])` / `dfs(s + "(")` | **不要** | 每层造新对象，O(长度) |
| **C 返回结果集** | 不传路径，每层返回「我这棵子树的全部答案」 | **不要** | 内存 = 所有结果同时在手 |



回溯记得copy当前的state到res，否则当前的state会被其他修改