# 560. Subarray Sum Equals K

### pass2

given prefix sum这个思路，我们先算再存，因为我们算和访问的都是前面的，不能自己配对。

相反，像sliding windows的扩左，每个新进来的element是都要被考虑的，先存再算.

---

- **「算」查的是谁**：查的是配对对象 `pre[i]`。配对对象必须严格在当前位置前面（`i < j`），所以查询那一刻，表里只能有 `pre[0..j-1]`。如果先存，表里就多了 `pre[j]` 自己。k=0 时 `pre[j]-k == pre[j]`，就配上了 `i == j` 的空子数组（`[1], k=0` → 1）。
- **滑窗为什么反过来**：新元素是从右边进来的（扩 r，上面写成了「扩左」）。窗口 `[l, r]` 是闭区间，本来就包含 r，所以要先把 `nums[r]` 放进窗口，再判断合不合法、要不要收缩 l。如果先判断再放，判断的就是 `[l, r-1]`，漏掉了当前元素。
- **统一成一句话**：查询时，当前元素属不属于被查的那个集合？
  - 不属于（配对，`i < j`）→ 先查后存：[1](../1.%20Two%20Sum/) / 560（本题）/ [974](https://leetcode.com/problems/subarray-sums-divisible-by-k/) / [525](https://leetcode.com/problems/contiguous-array/) / [219](https://leetcode.com/problems/contains-duplicate-ii/)
  - 属于（窗口含自己）→ 先存后查：[3](../3.%20Longest%20Substring%20Without%20Repeating%20Characters/) / [76](../76.%20Minimum%20Window%20Substring/) / [438](../438.%20Find%20All%20Anagrams%20in%20a%20String/) / [904](https://leetcode.com/problems/fruit-into-baskets/)，单调队列 [239](../239.%20Sliding%20Window%20Maximum/)
  - 要看全局 → 两遍扫，全存再查：[128](../128.%20Longest%20Consecutive%20Sequence/) / [242](../242.%20Valid%20Anagram/) / [387](https://leetcode.com/problems/first-unique-character-in-a-string/)
- **为什么平时测不出来**：顺序写反，只有在查询值等于当前值时才会出错，对 560 来说就是 k=0。所以写完先查后存的题，顺手用 k=0（或 target 等于 2x）测一下。


### pass1

1. 不能滑窗，如果元素>0可以，因为有数值方向，如果sum大了就缩左边界。但是这里元素有大有小，没有方向。
2. 对每个prefix存hash，内容是prefix_sum:counter
3. counter需要个占位的`prefix_sum_counter[0]=1 `
4. 先算prefix，查找prev_curr-prev_prev==k的，然后update res，再更新counter
5. 感觉是hash的集大成，2sum，3sum的高级版，若干sum