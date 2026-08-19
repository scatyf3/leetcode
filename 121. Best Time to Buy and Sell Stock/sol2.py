class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        '''
        Input: price list by day, range: 0 <= prices[i] <= 10^4
        Output: max profit
        greedy? build min array and max array range with time, and find solution using 2 array

        the key idea is that we do not need to explictly save the max min array
        just maintain the max/min during one for loop is enough
        '''
        # max_val = -1
        min_val = 10000000
        max_profit = -1

        for price in prices:
            if(price<min_val):
                min_val=price
            profit = price-min_val
            if(profit>max_profit):
                max_profit=profit
        return max_profit

'''

'''