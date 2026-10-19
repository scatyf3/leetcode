class Solution:
    def longestMountain(self, arr: list[int]) -> int:
        res = 0
        up = 0        # 当前这座山：上坡走了几步
        down = 0      # 当前这座山：下坡走了几步
        for i in range(1, len(arr)):
            if arr[i] > arr[i-1]:          # 上升
                if down > 0:               # 上一座山已经下过坡了 → 这是新山
                    up = 0
                    down = 0
                up += 1
            elif arr[i] < arr[i-1]:        # 下降
                if up > 0:                 # 前面有上坡，下坡才算数
                    down += 1
            else:                          # 平台：山断了
                up = 0
                down = 0

            if up > 0 and down > 0:        # 上下坡都有 → 完整的山
                res = max(res, up + down + 1)
        return res
