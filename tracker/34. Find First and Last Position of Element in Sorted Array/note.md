# 34. Find First and Last Position of Element in Sorted Array

大概思路知道，我们搜两个缝，一个右，一个左，然后处理edge case
1. 如果空列表会越界，先提前判
2. 如果elem不在，也会越界，判断第一个binary nums[l] 是否等于target，然后防止l这个右缝跑越界，俩检查 `l>=len(nums) or nums[l]!=target`