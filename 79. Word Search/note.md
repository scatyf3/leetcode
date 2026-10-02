# 79. Word Search

1. general的思路：grid search，然后这里的变化是dfs前后修改visited（回溯风格）
2. 感觉比较复杂，edit什么比较麻烦，这里修改一个nonlocal的变量。这里edit nonlocal比较省事，否则每层还要收集全部dfs再传
3. 就算edit nonlocal也要return，否则dfs继续往下，说越界了

