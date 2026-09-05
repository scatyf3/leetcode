from typing import List


class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        '''
        第二版: 完全背包求"所有具体方案"(非递归)。
        与 sol1 对照用, 实际提交仍推荐 sol1。
        '''
        # dp[t] = 用已经引入的物品凑出 t 的所有方案
        dp = [[] for _ in range(target + 1)]
        dp[0] = [[]]                       # 凑 0 有唯一方案: 空组合

        for c in candidates:               # 物品在外层 —— 去重靠这个
            for t in range(c, target + 1): # 容量正序 —— 允许重复取, 完全背包
                for comb in dp[t - c]:
                    dp[t].append(comb + [c])

        return dp[target]

        '''
        去重机制换人了: 不再是 start 下标, 而是"物品循环在外层"。
        每个 candidate 只在自己那一轮被引入, 天然固定了组合的生成顺序。

            物品外 / 容量内  -> 组合  (39, 518 零钱兑换 II)
            容量外 / 物品内  -> 排列  (377 组合总和 IV)
        这两行写反不会报错, 只会静默多出 [2,3,2] 这类重排, 是本写法唯一的大坑。

        为什么这题它输给回溯:
            dp[t] 存的是完整 list, comb + [c] 每次全量拷贝,
            且所有中间容量的方案都得一直留在内存里。
            回溯只共享一条 path, 命中时才拷贝一次。
            => 状态值是"计数/最值"时 DP 赢; 是"所有具体方案"时 DP 退化成
               把整棵搜索树物化在内存, 回溯赢。
        '''
