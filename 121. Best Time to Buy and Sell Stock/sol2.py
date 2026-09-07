class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        cur_min = 1000000
        max_profit = 0
        for i in range(len(prices)):
            max_profit = max(prices[i]-cur_min,max_profit)
            cur_min=min(cur_min,prices[i])
        return max_profit


