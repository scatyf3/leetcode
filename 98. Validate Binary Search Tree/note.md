
我想了一个局部比较，但是二叉搜索树要求root>left max，小于right min对吗

然后dfs里维护用参数left max和right min，return t/f即可，还不对，这和当前的sol不一致

两个办法
1. 维护祖先区间，left.val必定小于祖先区间，right.val大于祖先区间
2. 返回left max和right min，return t/f即可，当前node必须大于lmax小于rmin


思考，怎么做，我们有好多做法，我们直觉用sol3
1. 以bfs的min max，必须传参，valid传参也行，nonlocal也行。
2. 以none为basecase，否则太傻了，float('-inf') 是最大最小


| 文件 | 方向 | 怎么传信息 | 返回什么 | 能提前停吗 |
|---|---|---|---|---|
| sol.py | 从上往下 | 参数带着祖先给的区间 `(low, high)`，往左走收紧上界，往右走收紧下界 | `bool` | 能 |
| sol2.py | 按中序顺序 | `self.prev` 记住上一个访问的值，要求严格递增 | `bool` | 能 |
| sol3.py | 从下往上 | 不传参数，靠返回值把子树的最小值和最大值带上来 | `(ok, min, max)` | 不能，左右两边都得递归完 |

算不上"集大成"，更准确的说法是：它是树 DFS 三种信息流的样板题。一道题用三种写法都能做，而且每种都自然，这样的题不多，所以很适合拿来建立框架。