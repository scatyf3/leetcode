class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        # 3 index that sum=0
        # naive: 3 forloop
        # cache: 2 sum and it's index (value, value_pair)
        # remove dup?
        two_sum = {}
        n = len(nums)
        for i in range(n):
            j=i+1
            while j<n:
                sm = nums[i]+nums[j]
                if -sm in two_sum: # store the reverse value as key for fast search
                    two_sum[-sm].append([nums[i],nums[j]])
                else:
                    two_sum[-sm] = [[nums[i],nums[j]]]
                j+=1
        print(two_sum)
        res = []
        visited_value = set()
        for i in range(n):
            if nums[i] in two_sum and i not in visited_value:
                for pair in two_sum[nums[i]]:
                    # print(pair)
                    # print(nums[i])
                    res.append(pair+[nums[i]])
                visited_value.add(i)
        return res

        '''
        我的第一版 —— 【错解, 存档复盘用】。
        思路: 先把所有两数配对的"补数"存进哈希 (key = -(a+b)), 再拿每个数去查表凑成 0。
        方向是对的(2Sum 的哈希套路), 但落地时丢了下标, 错法有三层, 一层比一层深。

        --- 错误 1: 三个下标可能重合(根因, 去重救不了) ---
        哈希表里只存了**值** [nums[i], nums[j]], 没存下标。
        第三层拿 nums[k] 查表时, 查到的配对完全可能就包含 k 自己。
          nums = [-1, 2, 0]   正确答案: []  (无三元组)
          本解输出:            [[-1, 2, -1]]      <- 那个 -1 是下标 0, 既当配对的一半又当第三个数
          nums = [-1, 0, 1, 2, -1, -4]
          本解(排序去重后)还多出 (-4, 2, 2)       <- 数组里只有一个 2, 却用了两次
        约束 "i < j < k 三个下标互不相同" 从头到尾没有被表达出来。
        修法: 存 (i, j) 下标而不是值, 第三层只接受 j < k。

        --- 错误 2: 没有去重 ---
        同一组合会以不同顺序反复出现: [-1,2,-1] / [2,-1,-1] / [-1,-1,2]。
        nums = [0,0,0,0] 会输出 24 个 [0,0,0]。
        事后补救: res = {tuple(sorted(t)) for t in res}  (规范化 + set)
        但这是"先制造重复再擦掉", 见 sol2 的排序双指针 —— 那边压根不生成重复。

        --- 错误 3: visited_value 是死代码 ---
        名字叫 value 存的却是下标; 而 i 每轮都不同, 所以 `i not in visited_value` 恒为真。

        --- 还有一个过不去的硬伤: 空间 ---
        题目 n <= 3000, 两两配对有 n^2/2 ~ 4.5e6 个 pair, 全存进哈希会 MLE/TLE。
        这条决定了这个框架修好也不能用: O(n^2) 空间是结构性的, 不是调优能省掉的。

        --- 正解方向(见 sol2.py) ---
        排序 + 固定第一个数 + 相向双指针: O(n^2) 时间 / O(1) 空间。
        排序把"值相同"变成"位置相邻", 于是去重从全局问题塌成"跳过左右邻居"这个局部动作,
        而且下标天然满足 i < l < r, 错误 1 自动消失。
        内层双指针和 LC11 同族, 只是判断依据从"面积"换成"三数和与 0 比大小"。

        Test Cases (本解全错, 记录用):
        [-1,0,1,2,-1,-4] -> 期望 [[-1,-1,2],[-1,0,1]] | 本解给 12 个, 含假解 [-4,2,2]
        [-1,2,0]         -> 期望 []                    | 本解给 [[-1,2,-1]]
        [0,0,0,0]        -> 期望 [[0,0,0]]             | 本解给 24 个 [0,0,0]
        '''
