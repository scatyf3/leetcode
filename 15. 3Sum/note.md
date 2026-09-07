核心做法是先sort, 不能naive去重复，比如[0,0,0]去重后都没了

sort之后维护一个dup set，然后维护当前2sum的dup。

这里怎么保证防止重复三元组，而让[0,0,0]这种被正确记录？
被丢的只是"同一个值组合的第二次出现"

这玩意为啥不能用hash table？
1. 可以hash
2. 双循环，扫ij，内层循环同时 确定剩下的需要找补的数值 和 能不能找补，O(n^2)
3. 但是edge case如很多重复元素，会超时，需要加排序去重复。但感觉这样就不如跑西双指针了


怎么想到排序的？
1. 我的目标复杂度 ≥ O(n log n) 吗，这里肯定很复杂，排序下没啥坏处
2. 然后given这个单调性，用双指针逼近想要的东西，这里类似2sum和接水

说起来2 sum是双指针还是hash啊？
1. 无序用hash, O(n) < O(nlogn)
2. 有序用双指针，省空间，时间复杂度不变

---

感觉陷入suboptimal了，不纠结那个2sum hash的naive solution了，若这样做打补丁的心智复杂度更高。看`sol4`

naive的解
1. sort
2. fix第一个元素，剩下的部分退化为【需要去重的双指针】
3. 【需要去重的双指针】怎么做？目前不会。


```python
class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()                                   # ← 一切的前提
        n = len(nums)
        res = []
        for first_idx in range(n - 2): # 给下面两个pointer留空间
            if nums[first_idx] > 0:                           # 剪枝: 最小的都 > 0, 三个正数凑不出 0
                break
            if i > 0 and nums[first_idx] == nums[first_idx - 1]:      # 去重①: 第一个数跳过相邻重复
                continue

            l, r = first_idx + 1, n - 1                       # 下标天然满足 i < l < r, 不可能重合
            while l < r:
                total = nums[first_idx] + nums[l] + nums[r]
                if total < 0:
                    l += 1                            # 和偏小 -> 左指针右移(取更大的数)
                elif total > 0:
                    r -= 1                            # 和偏大 -> 右指针左移(取更小的数)
                else:
                    res.append([nums[first_idx], nums[l], nums[r]])
                    l += 1
                    while l < r and nums[l] == nums[l - 1]:   # 去重②: 跳过和上一个相同的左值
                        l += 1
        return res
```

不过有序的2 sum替我把去重给跳过了，保证只有一组...

一个挖空版本
```python
class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()                                   # ← 一切的前提
        n = len(nums)
        res = []
        for first_idx in range(n - 2): # 给下面两个pointer留空间
            if # early exit
            if # remove dup

            l, r = #
            while l < r:
                total = nums[first_idx] + nums[l] + nums[r]
                if #
                elif #
                else:
                    #
                    while 
        return res
```