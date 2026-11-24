class Solution:
    def findRadius(self, houses: list[int], heaters: list[int]) -> int:
        heaters.sort()                          # bisect 要求有序
        nearest_heater_dis = []

        for h in houses:
            # 第一个 >= h 的 heater，idx 在 0..len(heaters) 之间
            idx = bisect_left(heaters, h)
            best = float('inf')

            if idx < len(heaters):              # 右边有 heater
                best = min(best, heaters[idx] - h)     # 右边减 h，结果 >= 0
            if idx > 0:                         # 左边有 heater
                best = min(best, h - heaters[idx - 1]) # h 减左边，结果 > 0

            nearest_heater_dis.append(best)

        return max(nearest_heater_dis)          # 最难覆盖的 house 决定半径
