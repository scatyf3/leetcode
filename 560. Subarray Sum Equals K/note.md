# 560. Subarray Sum Equals K

1. 不能滑窗，如果元素>0可以，因为有数值方向，如果sum大了就缩左边界。但是这里元素有大有小，没有方向。
2. 对每个prefix存hash，内容是prefix_sum:counter
3. counter需要个占位的`prefix_sum_counter[0]=1 `
4. 先算prefix，查找prev_curr-prev_prev==k的，然后update res，再更新counter
5. 感觉是hash的集大成，2sum，3sum的高级版，若干sum