class Solution:
    def canCompleteCircuit(self, gas: list[int], cost: list[int]) -> int:
        change = []
        for i in range(len(gas)):
            change.append(gas[i]-cost[i])
        if sum(change)<0:
            return -1
        # prefix sum的最低点
        # 被corner case带偏了，左边就是比右小
        # [2,-1,-1] => index=2 => 3 % 3 =0
        # 这里的操作就是取模
        left_accu = 0
        min_left = 0
        min_index = -1
        for l in range(len(change)):
            left_accu += change[l]
            if left_accu < min_left:
                min_left = left_accu
                min_index = l
        return (min_index + 1) % len(change)
