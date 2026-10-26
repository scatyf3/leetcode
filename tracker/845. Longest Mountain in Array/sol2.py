class Solution:
    def longestMountain(self, arr: list[int]) -> int:
        res = 0
        up = 0
        down = 0
        # state machine 00 -> 10 -> 11 -> 10 / 00
        cur = 0  # 当前山的边数, 元素数 = cur + 1
        for i in range(1, len(arr)):
            if arr[i-1] < arr[i]:  # increase
                if up == 0 and down == 0:
                    up = 1
                    cur = 1
                elif up == 1 and down == 0:
                    cur += 1
                elif up == 1 and down == 1:
                    # 谷底同时是新山的起点: 这一步就是新山的第一段上坡
                    down = 0
                    cur = 1
            elif arr[i-1] > arr[i]:  # decrease
                if up == 1:  # 10 -> 11, 或 11 留在 11
                    down = 1
                    cur += 1
                    res = max(res, cur + 1)  # 处在 11 就是合法的山, 当场结算
                # 00 碰到下降: 留在 00, 不用管
            else:  # equal
                up = 0
                down = 0
                cur = 0
        return res
