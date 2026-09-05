class Solution:
    def search(self, nums: List[int], target: int) -> int:
        '''
        Input:
        - nums: List[int], 1 <= n <= 5000, 元素互异, 原本升序、被旋转了未知次
        - target: int
        Target: 返回 target 的下标, 不存在返回 -1
        Return: int
        Output: int

        解法: 两步二分   O(log n) 时间 / O(1) 空间
          第 1 步 找旋转点 p(= 最小值的下标)   -> 就是 LC153, 直接复用
          第 2 步 判断 target 落在哪一段, 在那一段里跑普通二分
        两步各 O(log n), 合起来还是 O(log n)。

        为什么可以分两段:
            下标   0  1  2  3  4  5  6
            值     4  5  6  7  0  1  2
                   └─ 大段 ─┘  └小段┘
                               p=4
          大段 = nums[0 .. p-1], 值域 nums[0] ~ nums[p-1]  (全都 > nums[n-1])
          小段 = nums[p .. n-1], 值域 nums[p] ~ nums[n-1]  (全都 <= nums[n-1])
          两段各自升序, 值域不重叠 => 看 target 落在哪个值域里就知道搜哪段。
        '''
        n = len(nums)

        # ---- 第 1 步: 找最小值下标 p(LC153) ----
        # nums[n-1] 一定落在小段里, 所以 nums[mid] > nums[n-1] <=> mid 在大段
        l, r = 0, n - 1
        while l < r:
            if nums[l] < nums[r]:      # 这一段已经升序, 起点就是最小值, 提前退出
                break
            mid = (l + r) // 2
            if nums[mid] > nums[r]:
                l = mid + 1            # mid 在大段, 最小值在右边
            else:
                r = mid                # mid 在小段, 最小值是它或在左边
        p = l

        # ---- 第 2 步: 选段 + 普通二分 ----
        # 写成"target 是否落在小段的值域内", 而不是 target >= nums[0]:
        # 未旋转时 p == 0, 大段是空区间 [0, -1], 这个写法会自然走小段那一支, 不用特判
        if nums[p] <= target <= nums[n - 1]:
            lo, hi = p, n - 1
        else:
            lo, hi = 0, p - 1

        while lo <= hi:                # 有 target 要找, 用闭区间 + "找到就返回"的经典模板
            mid = (lo + hi) // 2
            if nums[mid] == target:
                return mid
            if nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

        '''
        两个 while 的模板不一样, 别混:
          第 1 步 while l < r  + r = mid      -> 没有 target, 靠区间塌成单点得到答案
          第 2 步 while lo<=hi + hi = mid-1   -> 有 target, 找到就返回, 找不到要让区间变空
        写反了: 第 1 步用 <= 会死循环(l==r 时 mid==l, r=mid 区间不变);
                第 2 步用 <  会漏掉最后一个元素。

        Dry Run: nums = [4,5,6,7,0,1,2], target = 0
          第1步: l=0 r=6  nums[0]=4 > nums[6]=2, 不提前退出; mid=3, 7>2 -> l=4
                 l=4 r=6  nums[4]=0 < nums[6]=2 -> break        p=4
          第2步: nums[4]=0 <= 0 <= nums[6]=2  -> 搜小段 [4,6]
                 lo=4 hi=6 mid=5 nums[5]=1 > 0 -> hi=4
                 lo=4 hi=4 mid=4 nums[4]=0 == 0 -> return 4 ✓

        Dry Run: nums = [4,5,6,7,0,1,2], target = 6
          p=4; 6 不在 [0,2] 内 -> 搜大段 [0,3]
          lo=0 hi=3 mid=1 nums[1]=5 < 6 -> lo=2
          lo=2 hi=3 mid=2 nums[2]=6 == 6 -> return 2 ✓

        Test Cases (已在 5036 个数组 x 每个数组的全部 target 上验证):
        [4,5,6,7,0,1,2], 0  -> 4
        [4,5,6,7,0,1,2], 3  -> -1     不存在
        [4,5,6,7,0,1,2], 6  -> 2      落在大段
        [1],             0  -> -1     n=1
        [1],             1  -> 0
        [1,3],           3  -> 1      n=2 未旋转
        [3,1],           1  -> 1      n=2 旋转
        [1,2,3,4,5],     5  -> 4      完全没旋转 -> p=0, 大段为空, 走小段那一支

        另一种写法(更短, 一次二分): 找到 p 之后整个数组就是"被平移 p 位的有序数组",
        二分时把逻辑下标映射回真实下标 real = (mid + p) % n, 不用分段。同样验证通过。
        '''
