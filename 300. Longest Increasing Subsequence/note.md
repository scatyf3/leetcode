# 300. Longest Increasing Subsequence

并非双指针，可以跳选，subseq是cs固定的描述「可跳跃的子切片」的术语
这里是dp？，存「截止到当前index最大递增序列」 的长度
dp[i] = 以 nums[i] 结尾的最长上升子序列长度 ✓

### O(n^2) DP

但是有edge case，我的naive solution 好像无法


这里仍然是有两个解法：
1. sol的优雅解，dp init with 1
2. 我的dp，好像也是对的，然而max错了，错在哪里？

不对啊，第一步不是
 dp[i]=max(dp[i],dp[j]+1)

 i=1, j=0，此时不是dp[1]=max(-114, 1) 吗

---

哨兵被读了 7 次。

关键在这句：for i / for j 保证的是「j 在 i 之前被处理过」，不保证「dp[j] 被赋值过」。 赋值那行外面还套着 if nums[i] > nums[j]。

TLDR: dp 数组init成「单独」的正确解而不是拍脑袋的负数?

不完全是，可以用哨兵但是检查
```python
if nums[i] > nums[j] and dp[j] != -114:      # 显式检查
    dp[i] = max(dp[i], dp[j] + 1)
```

要么用真值初始化（然后可以直接参与运算），要么用哨兵（然后每次读之前必须显式检查）。不能只写哨兵不检查。

以及，「单独」是这题的措辞，通用说法是「零次转移」

### Followup

核心是换一个存储对象 —— 不再存「以 i 结尾的长度」，而是存 tails[k] = 所有长度为 k+1 的上升子序列中，最小的那个结尾：

```python
from bisect import bisect_left

class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        tails = []
        for x in nums:
            i = bisect_left(tails, x)      # 第一个 >= x 的位置
            if i == len(tails):
                tails.append(x)            # x 比所有结尾都大 -> 能接在最长的后面, 长度 +1
            else:
                tails[i] = x               # 否则把这一档的结尾换小, 给后面留更多机会
        return len(tails)
```

bisect_left(a, x) = 在有序列表 a 里，找 x 应该插进去的最左位置 —— 等价于「第一个 ≥ x 的元素的下标」。

这个api的底层实现是啥，二分查找吗？
对

tldr
1. 对每个元素，找 第一个大于等于次元素的index
2. 如果此元素是第一个，则纳入subseq，如果不是则skip吗。如果每个元素都是第一个出现，一定是最长的吗，还是其他的性质？ 并非，让agent举个例子

```
=== [5,6,1,2,3] ===
   x  分支       tails            含义
   5  append   [5]              比所有结尾都大 -> 新开长度 1 这一档
   6  append   [5, 6]           比所有结尾都大 -> 新开长度 2 这一档
   1  replace  [1, 6]           长度 1 这一档的门槛从 5 降到 1(答案不变, 给后面留机会)
   2  replace  [1, 2]           长度 2 这一档的门槛从 6 降到 2(答案不变, 给后面留机会)
   3  append   [1, 2, 3]        比所有结尾都大 -> 新开长度 3 这一档
答案 = 3

如果把 replace 真的当成"skip"(只在 append 时才收):
  -> [5, 6] 长度 2   <- 少了! 真实 LIS 是 [1,2,3] 长度 3

=== [10,9,2,5,3,7,101,18] ===
   x  分支       tails            含义
  10  append   [10]             比所有结尾都大 -> 新开长度 1 这一档
   9  replace  [9]              长度 1 这一档的门槛从 10 降到 9(答案不变, 给后面留机会)
   2  replace  [2]              长度 1 这一档的门槛从 9 降到 2(答案不变, 给后面留机会)
   5  append   [2, 5]           比所有结尾都大 -> 新开长度 2 这一档
   3  replace  [2, 3]           长度 2 这一档的门槛从 5 降到 3(答案不变, 给后面留机会)
   7  append   [2, 3, 7]        比所有结尾都大 -> 新开长度 3 这一档
 101  append   [2, 3, 7, 101]   比所有结尾都大 -> 新开长度 4 这一档
  18  replace  [2, 3, 7, 18]    长度 4 这一档的门槛从 101 降到 18(答案不变, 给后面留机会)
答案 = 4
```

tail就是那个要的切片是吗，tail有点像 slot，有两个操作，append和replace，只能replace tail，找到更小的，为未来留出空间的选择，这个理解对吗？ 

不对，tail到底存的value还是index？
长度为x的最小结尾value

