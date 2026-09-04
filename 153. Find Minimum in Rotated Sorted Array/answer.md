二分，拿 `nums[mid]` 和 **`nums[r]`** 比：大于说明最小值在右半（`l = mid+1`），否则在左半含 mid（`r = mid`）。

⚠ 必须和 `nums[r]` 比不能和 `nums[l]` 比；`r = mid` 不能写 `mid-1`（mid 可能就是答案）。
