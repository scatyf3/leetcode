from typing import List


class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()          # 只为剪枝, 防止内容一样，然而顺序不一样的切片进入答案
        res = []
        path = []                #  当前这条路径上已经选了哪些数，一个tmp遍历

        def dfs(start: int, remain: int) -> None: 
            # start => 这一层只许从 candidates[start] 往后挑，是候选区间的左边界
            # remain => 还剩多少凑够target
            if remain == 0: # 递归的停止条件, 
                res.append(path[:])   # 必须拷贝, 否则存进去的是同一个会被改空的 list
                return
            for i in range(start, len(candidates)):
                if candidates[i] > remain:
                    break              # 已排序, 后面只会更大, 直接断掉整层
                path.append(candidates[i])
                dfs(i, remain - candidates[i])  # 是 i 不是 i+1: 允许重复取自己
                path.pop()                      # 撤销, 恢复现场

        dfs(0, target)
        return res

        '''
        去重机制: start 下标不回头, 强制每个组合只按"下标非递减"这一种顺序生成,
                  所以 [2,3] 只会以 (i=0, i=1) 出现一次, 不会有 [3,2]。
                  这与数组是否有序无关 —— sort 只负责让 break 成立。

        复杂度: 时间 O(N^(T/M)) —— 搜索树分支 N, 深度最多 T/M (M = 最小候选值),
                     下界由输出规模决定, 无法更优
                空间 O(T/M) 递归栈 + path (不计返回值)

        Dry Run: candidates=[2,3,6,7], target=7
            2 -> 2 -> 2 -> (remain=1, 2>1 break)
                   -> 3 -> remain=0  => [2,2,3]  ✓
            2 -> 3 -> (remain=2, 但 start=1, 3>2 break)
            7 -> remain=0 => [7]  ✓
            答案 [[2,2,3],[7]]
        '''
