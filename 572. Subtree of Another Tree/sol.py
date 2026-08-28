# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        '''
        Target: root 里是否存在某个节点,以它为根的子树和 subRoot 完全相同
        Return: bool

        这题 = 树上的子串匹配。必须两个递归,因为两者的"步进方式"相反:
            判同 dfs(a,b)     : 两棵树同步下降,子结果用 and(左右都得对上)
            搜索 isSubtree    : 只有大树下降,subRoot 钉死在根,子结果用 or(哪儿对上都算)
        一个函数只能有一种步进方式。写成一个 dfs + if/else 会在"值相等"那一刻
        把 subRoot 拆开,之后就再也拿不到完整的 subRoot 去别处试了。

        复杂度 O(m*n) —— 外层每访问一个节点就启动一整轮内层递归。
        '''
        def dfs(root, subroot):                  # 语义收窄:两棵树完全相同?
            # base case 必须覆盖两个参数的 2x2 空/非空组合,漏一格就会掉到
            # root.val / subroot.val 上炸掉。写完机械地对一遍这张表:
            #
            #   root  | subroot |  该返回          | 谁接住
            #   ------|---------|-----------------|------------------
            #   None  | None    |  True(都走完)   | 第 1 个 if
            #   非空  | None    |  False(root多)  | 第 1 个 if   <- 最容易漏这格
            #   None  | 非空    |  False(root少)  | 第 2 个 if
            #   非空  | 非空    |  继续往下比      | 落到 root.val
            #
            # 坑:`if X is None` 只拦得住 X 为空,另一个参数为空时照样漏过去。
            # 把第 1 个写成 `if root is None: return subroot is None` 就只覆盖了
            # 上表第 1、3 行,第 2 行(root 非空 subroot 空)直接掉到 subroot.val ->
            # AttributeError,而且此时第 2 个 if 变成永远进不来的死代码。
            #
            # 想不依赖顺序的话用这个对称写法,一行收掉前三格:
            #   if root is None or subroot is None:
            #       return root is None and subroot is None
            if subroot is None:
                return root is None              # subroot 走完不等于成功,root 也得同时走完
            if root is None and subroot is not None:
                return False
            if root.val == subroot.val:
                return dfs(root.left, subroot.left) and dfs(root.right, subroot.right)
            else:
                return False                     # 值不等就是不同;搜索逻辑不在这里

        # 搜索层:先在当前节点判同,不成再去左右子树找。
        # 关键是 or 而不是 if/else —— "先试 A,A 不成再试 B",and 是不能回头的
        if root is None:
            return subRoot is None
        return (dfs(root, subRoot)
                or self.isSubtree(root.left,  subRoot)
                or self.isSubtree(root.right, subRoot))

        '''
        Dry Run: root = 2 -> 左2 -> 左3 ,  subRoot = 2 -> 左3
        A(2) 处 dfs(A, S): 2==2 -> dfs(B, T(3)) 值 2!=3 -> False,整体 False
        不成,继续 self.isSubtree(A.left=B, S)
        B(2) 处 dfs(B, S): 2==2 -> dfs(C(3),T(3)) True and dfs(None,None) True -> True
        => True   (若在 A 处 if/else 二选一,这里就找不到了)

        Test Cases:
        [3,4,5,1,2] / [4,1,2]              -> True
        [3,4,5,1,2,N,N,N,N,0] / [4,1,2]    -> False  子树多挂了个 0,不是前缀匹配
        [1,2] / [1]                        -> False  子树须含全部后代
        [2,N,1] / [1]                      -> True   右子树也要搜
        [2,2,N,3] / [2,3]                  -> True   顶上值相等但配不上,须继续往下找
        [] / [1]                           -> False
        '''
