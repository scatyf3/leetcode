class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        '''
        Input:
        - nums: List[int], 3 <= n <= 3000, -1e5 <= nums[i] <= 1e5
        Target: 所有和为 0 且下标互不相同的三元组, 结果不含重复三元组
        Return: List[List[int]]
        Output: list of triplets

        解法: 排序 + 固定第一个数 + 内层哈希查"补数"   O(n^2) 时间 / O(n) 空间
        和 sol3 等价, 区别只在哈希表存什么:
          sol3   seen 存"已走过的值",     查询时现算 c = -(nums[i]+nums[j])
          本版   remain_map 存"还需要的补数", 查询时直接问 nums[i] 在不在表里
        两种写法信息量相同(互为反演), 选哪个纯看顺手。

        --- 这一版是从一个错解迭代出来的, 改动记在这里 ---
        初版三个 bug, 逐个修:
          1. 内层写成 range(fix_start, n)  -> 下标重合, 假解      [已修: +1]
          2. res 是 list, 没有任何去重      -> 重复三元组          [已修: 去重①]
          3. sort() 排了却没利用            -> 重复元素多时 TLE    [已修: 去重① + 剪枝]

        错误 1 展开(它和 sol1 的"错误 1"同源, 只是换了个门进来):
          i == fix_start 那一圈会写入 remain_map[target - nums[f]] = remain_map[-2*nums[f]],
          等于把"固定的那个数自己"当成候选配对种进了表。
          后面撞上任何等于 -2a 的值就命中, 产出 [a, a, -2a] —— 和是 0, 但 a 只有一份。
            [-2, 1, 4] -> [[-2,-2,4]]   期望 []
            [-1, 2, 0] -> [[-1,-1,2]]   期望 []      <- sol1 注释里记的同一个反例
          不变量: 表里的东西必须严格来自 (fix_start, i) 开区间。起点写 fix_start 就破坏了它。
          note: sol2 总结的"先查后加, 顺序不能反"这一版是遵守了的, 漏在了循环起点上。
        '''
        n = len(nums)
        res = []
        nums.sort()                                   # 去重① 和剪枝都依赖它
        for fix_start in range(n - 2):
            # we need at least 2 elem for inner interations
            if nums[fix_start] > 0:                   # 剪枝: 最小的都 > 0, 三个正数凑不出 0
                break
            if fix_start and nums[fix_start] == nums[fix_start - 1]:
                continue                              # 去重①: 跨 fix_start, 和左邻居比 -> 保留第一份

            remain_map = {}                           # remain -> index (index 其实没用到, set 也行)
            dup = set()                               # 去重②: 同一个 fix_start 内已收过的 nums[i]
            target = 0 - nums[fix_start]
            for i in range(fix_start + 1, n):         # 这里要 +1 否则 nums[fix_start] 会被自己复用
                if nums[i] in remain_map and nums[i] not in dup:
                    res.append([nums[fix_start], target - nums[i], nums[i]])
                    dup.add(nums[i])
                remain = target - nums[i]
                remain_map[remain] = i
        return res

        '''
        为什么 dup 只存 nums[i] 就够, 不用像 sol3 那样存 (c, nums[j]) 整个 pair:
          fix_start 一旦固定, target 也固定, 于是三元组
              [nums[f], target - nums[i], nums[i]]
          完全是 nums[i] 的函数 => nums[i] 相同 <=> 三元组相同。存一个数即可。

        两个去重点缺一不可(sol3/sol4 注释里已验证过, 这里同样成立):
          只有① 没有②: [0,0,0,0]   会输出两遍 [0,0,0]   (remain_map[0] 被覆盖后反复命中)
          只有② 没有①: [-1,-1,0,1] 会输出两遍 [-1,0,1]  (两个 -1 各当了一次第一个数)
        去重① 必须和 nums[i-1] 比, 不能和 nums[i+1] 比:
          比 i+1 的语义是"后面还有同样的值, 留给它做", 但 fix_start 只跑到 n-3, 最后一份轮不到,
          结果没人干 -> [0,0,0] 和 [0,0,0,0] 都会返回 []。去重要保留第一次出现, 不是最后一次。

        Dry Run: nums = [-1,0,1,2,-1,-4]  ->  排序后 [-4,-1,-1,0,1,2]
        f=0 (-4): target=4, 逐个存补数 5,5,4,3,2; 没有 nums[i] 命中 -> 无解
                  (要两数和为 4, 但 -1,-1,0,1,2 里凑不出)
        f=1 (-1): target=1
                  i=2 (-1): -1 不在 m{}        -> m[2]=2
                  i=3 (0):  0  不在 m{2}       -> m[1]=3
                  i=4 (1):  1  **在** m{2,1}   -> 收 [-1, 0, 1]  ✓  dup={1}
                  i=5 (2):  2  **在** m{2,1,0} -> 收 [-1,-1, 2]  ✓  dup={1,2}
        f=2 (-1): nums[2]==nums[1] -> continue        <- 去重①, 否则上面两个解再产一遍
        f=3 (0):  target=0, 补数 -1,-2; 无命中 -> 无解
        return [[-1,0,1], [-1,-1,2]]

        实测 (n=3000, 本地):
        | 写法                        | [0]*3000 |
        |-----------------------------|----------|
        | 不去重, res 是 list          | 1.48s, 输出 4498499 条(还是错的) |
        | res 换 set(边生成边 add)     | 0.53s    |
        | 本版(去重① + 去重②)          | 0.00s    |
        | sol4 双指针                  | 0.00s    |
        换 set 只要改 3 处、不用想去重方向, 但它是"先造 450 万个重复再擦掉";
        去重① 是让它们压根不产生。本地 0.5s 在 LeetCode 上很悬, 所以选后者。

        和 sol4 的取舍(结论没变):
          时间同为 O(n^2); 本版空间 O(n)(remain_map + dup), sol4 是 O(1)。
          排序的钱已经付了, 双指针就是免费升级 —— 下标天然 i < l < r, 错误 1 结构性地不可能发生,
          去重也塌成"跳过邻居"一个局部动作, 不需要 dup 集合。
          所以标准答案仍是 sol4, 本版的价值是把哈希路线走到了能过题的形态。

        Test Cases (已与 sol4 随机对拍 3000 组, 结果一致):
        [-1,0,1,2,-1,-4] -> [[-1,0,1],[-1,-1,2]]
        [-2,1,1,1]       -> [[-2,1,1]]       只出现一次(去重②)
        [0,0,0,0]        -> [[0,0,0]]        只出现一次(去重① + ②)
        [0,0,0]          -> [[0,0,0]]        <- 去重方向写反(比 i+1)的话这里会变成 []
        [-1,-1,0,1]      -> [[-1,0,1]]       只出现一次(去重①)
        [-2,1,4]         -> []               <- 初版在这里给假解 [[-2,-2,4]]
        [-1,2,0]         -> []               <- 初版在这里给假解 [[-1,-1,2]]
        [0,1,1]          -> []
        [-2,0,1,1,2]     -> [[-2,1,1],[-2,0,2]]
        [0]*3000         -> [[0,0,0]]        0.00s
        '''
