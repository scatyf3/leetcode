class Solution:
    def carFleet(self, target: int, position: list[int], speed: list[int]) -> int:
        # 按起点从大到小：先处理离终点最近的车
        arr = sorted(zip(position, speed), reverse=True)

        fleets = 0
        cur = 0.0  # 当前最前面那个车队的到达时间
        for pos, sp in arr:
            t = (target - pos) / sp
            if t > cur:
                # 追不上前面的车队 -> 自己开一个新车队
                fleets += 1
                cur = t
            # t <= cur: 被堵在后面，并入当前车队，cur 不变
        return fleets
