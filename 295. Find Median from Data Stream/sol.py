class MedianFinder:
    '''
    if insert, l or right
    move index, insert val, update curr median

    思路: 维护一个始终有序的数组。二分找到插入位置,插进去,
          再更新中位数下标。addNum O(n) (insert 要挪元素), findMedian O(1)。
    '''

    def __init__(self):
        self.n = 0
        self.curr_median_left_index = 0
        self.curr_median_right_index = 0
        self.arr = []

    def addNum(self, num: int) -> None:
        idx = self.binary_search(num)      # 二分找插入位置
        self.arr.insert(idx, num)          # 插入
        self.n += 1                        # ★ 别忘了,否则 binary_search 的 r 永远是 -1
        # 更新中位数下标:只跟 n 有关,跟 num 插在哪、num 多大都无关
        self.curr_median_left_index = (self.n - 1) // 2
        self.curr_median_right_index = self.n // 2

    def binary_search(self, num: int) -> int:
        # 返回 num 应该插入的下标。搜索的是"缝"不是"元素",所以 r 取 n 不是 n-1
        l, r = 0, self.n
        while l < r:                       # 区间 [l, r) 为空时停
            mid = (l + r) // 2             # ★ mid 在循环内算,只算这一处
            if self.arr[mid] <= num:
                l = mid + 1                # ★ 写 l = mid 会死循环
            else:
                r = mid
        return l                           # ★ 返回 l,不是 mid

    def findMedian(self) -> float:
        # n 为奇数时 left == right,取到同一个元素,平均后还是它自己
        return (self.arr[self.curr_median_left_index]
                + self.arr[self.curr_median_right_index]) / 2


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()


# ============================================================
# 这版是从一个全崩的初稿改出来的,五个坑记一下
# ============================================================
#
# 初稿跑 addNum(1),addNum(2),addNum(3) 的实际结果:
#     arr=[1]        L=-2  R=0  n=0   findMedian -> IndexError
#     arr=[2, 1]     L=-4  R=0  n=0   findMedian -> IndexError
#     arr=[2, 3, 1]  L=-6  R=0  n=0   findMedian -> IndexError
# 数组没排序,L 一路跑负,R 从头到尾没动过。
#
#
# ---- 1. self.n 忘了 +=1 --------------------------------------
# n 恒为 0 -> binary_search 里 r = -1 -> while 0 < -1 不成立 ->
# 直接返回 mid = (0 + -1)//2 = -1 -> arr.insert(-1, num) 插在倒数第二位。
# 这一个 bug 同时毁掉了二分和数组有序性。
#
#
# ---- 2. 二分的搜索空间是"缝",r 取 n ---------------------------
# 长度 3 的数组有 4 条缝: _1_2_3_  下标 0..3。
# r = n-1 会让 "追加到末尾" 这个合法答案根本不可达。
# 同一个思维模式在 139. Word Break 里出现过("节点是缝不是字符")。
#
#
# ---- 3. l = mid 会死循环 --------------------------------------
# while l < r 要求每次迭代区间真的缩小。r == l+1 时 mid == l,
# 写 l = mid 等于原地踏步。
# 开闭要配对: 区间 [l, r) 左闭 -> l 跳过 mid (mid+1);
#                        右开 -> r 停在 mid (mid 还可能是答案)。
#
#
# ---- 4. mid 不要算两遍 ----------------------------------------
# 初稿在循环前算一次、循环体末尾又算一次。同一个值有两个计算点,
# 改的时候漏一处就出错。
#
#
# ---- 5. 三个 if/elif/else 分支是伪需求,只能删不能修 -------------
# 初稿想"比较 num 和当前中位数,再决定下标往哪挪"。但:
#
#     插入前:  left = (n-1)//2      right = n//2
#     插入后:  left = n//2          right = (n+1)//2
#
# 新下标里没有 num,也没有 idx —— 中位数的【下标】只由元素个数决定,
# num 插在最左还是最右,下标该怎么挪都一样。变的是那个位置上存的【值】。
# 所以那个分支假设了一个不存在的依赖,加减号怎么调都调不对。
#
#
# ---- 冗余状态的代价 -------------------------------------------
# self.n 和 len(self.arr) 是同一个信息的两份拷贝,bug 1 就是它俩不同步。
# curr_median_left/right_index 同理,现在是 self.n 的纯函数。
# 三个字段都能删掉、findMedian 里现算。留着纯粹是为了保持原结构。
# 教训: 能 O(1) 算出来的东西别存成字段,存了就得在每个修改点同步它。
