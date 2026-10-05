# 79. Word Search

### pass2

为啥我们edit nonlocal的find就那么麻烦，它返回就比较省事啊？
1. 之前的sol只从start列表调，所以先进去再检查
2. 第二版如果要删掉start列表，检查就很麻烦...

agent说推荐第一种

### pass1
1. general的思路：grid search，然后这里的变化是dfs前后修改visited（回溯风格）
2. 感觉比较复杂，edit什么比较麻烦，这里修改一个nonlocal的变量。这里edit nonlocal比较省事，否则每层还要收集全部dfs再传
3. 就算edit nonlocal也要return，否则dfs继续往下，说越界了

