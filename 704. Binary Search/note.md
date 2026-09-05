1. while状态必须l<=r，这里要防止的edge case是len(nums)==1
2. 递推的时候需要skip自己防止死循环, l=mid+1, r=mid-1
3. 记得fp转int，用`//`