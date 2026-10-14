class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        '''
        1. integer array prices where prices[i] is the price of a given stock on the ith day
        2. action: 
            1. buy
            2. hold
            3. sell
            4. sell and buy
        
        intuition: benifit from all positive diff, 无限次交易时，"吃所有上坡" ≥ "只吃头尾"
        [3,2,1]
        '''
        profit = 0
        n = len(prices)
        for i in range(1,n): # python -1 do not has out of range error for i in range(0,n), nums[i-1] is nums[-1] 
            if(prices[i-1]<prices[i]):
                profit+=prices[i]-prices[i-1]
                print(prices[i]-prices[i-1])
        return profit


