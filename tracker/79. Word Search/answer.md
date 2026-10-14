网格 DFS + 回溯：每格当起点，`visited` 进去加、回来删（别的路径还可能经过这格）。要的是「有没有」，`dfs` 返回 bool，`if dfs(...): return True` 往上传，找到就停。

⚠ 匹配完要 `return`，否则接着读 `word[len(word)]` 越界；`set(pair)` 会把元组拆开，起点要 `{pair}`。
