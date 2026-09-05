class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        '''
        Input:
        - candidates: List[int], 1 <= len <= 30, 2 <= candidates[i] <= 40, 元素互不相同
        - target: int, 1 <= target <= 40
        Target:
        找出所有和为 target 的组合;同一个数可以重复选无限次
        Behavior:
        搜索,不修改输入(sort 会原地改,介意的话先 copy)
        Return:
        List[List[int]],组合内顺序不限,组合之间不能重复
        Output: e.g. [2,3,6,7], 7 -> [[2,2,3],[7]]
        '''
        candidates.sort()          # 可选:排序后剪枝能从 continue 升级成 break
        res, path = [], [] # path： tmp的切片

        def backtrack(start: int, remain: int) -> None:
            # start => 这一层允许从 candidates 的哪个下标开始往后挑
            # ramain => 离想要的sum还差多少
            if remain == 0:
                res.append(path[:])
                return
                

            # 只从 start 往后选:保证组合内下标单调不减,天然去掉顺序重复
            for i in range(start, len(candidates)):
                # start的数值大于剩下的，不可能再有解了
                if(candidates[start]>remain):
                    return
                # 相当于一个tree fanout的一堆option
                path.append(candidates[i]) # 增加
                backtrack(i,remain-candidates[i])
                path.pop() # 撤销，即同node fanout

        backtrack(0, target)
        return res
    
        '''
        Dry Run:
        Test Cases:
        - [2,3,6,7], 7   -> [[2,2,3],[7]]
        - [2,3,5], 8     -> [[2,2,2,2],[2,3,3],[3,5]]
        - [2], 1         -> []          # 剪枝直接把根砍掉
        - [8], 8         -> [[8]]       # 单元素刚好命中
        '''


# ============================================================
# 骨架:回溯就三行
# ============================================================
#
#     path.append(x)        # 做选择
#     backtrack(下一层)      # 递归
#     path.pop()            # 撤销选择  ← "回溯"这个名字就是指这一行
#
# 三个必须自己想清楚的参数:
#   1. 什么时候收答案?          -> remain == 0
#   2. 下一层从哪个下标开始?     -> i (不是 i+1),因为可以重复选同一个数
#   3. 什么时候不用往下走了?     -> candidates[i] > remain
#
#
# ---- start 是怎么防重复的 ----------------------------------
#
# 要防的不是"输入里的重复数字"(题目保证 distinct),而是
# [2,2,3] / [2,3,2] / [3,2,2] 这种顺序不同的同一个组合。
#
# for i in range(start, n) 保证组合里的下标单调不减:
#     选了 2 -> 下一层 start=0,还能选 2,3,6,7
#     选了 3 -> 下一层 start=1,只剩 3,6,7    ← 2 被永久排除
# 所以 [3,2,2] 这条路根本不会生成。
# 如果写成 range(0, n),三份全都会冒出来。
#
#
# ---- 两个必踩的坑 ------------------------------------------
#
# 1) res.append(path)  ×      res.append(path[:])  √
#    path 是同一个 list 被反复 append/pop,存引用的话
#    回溯结束后 res 里全是空列表。
#
# 2) 递归传 i+1 是 40 题(每个数只用一次)的形状,不是 39。
#
#
# ---- sort 要不要? ------------------------------------------
#
# 可选。排序只是为了把剪枝从 continue 升级成 break
# (有序时 candidates[i] > remain 意味着后面全都更大,可以整段砍掉)。
# 不排序写 continue 也完全正确。
#
# 真正"必须 sort + 去重"的是 40. Combination Sum II:输入有重复数字,
# 且每个数只能用一次,那时要加同层去重:
#     if i > start and candidates[i] == candidates[i-1]: continue
# 注意是 i > start 不是 i > 0 —— i == start 是这一层的第一个选择,必须放行。
