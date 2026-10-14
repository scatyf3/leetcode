class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        '''
        Input: price list by day, range: 0 <= prices[i] <= 10^4
        Output: max profit
        greedy? build min array and max array range with time, and find solution using 2 array
        '''
        min_price=[]
        max_price=[]
        # find min in 0->n order
        for idx in range(0,len(prices)):
            if(idx==0):
                min_price.append(prices[idx])
            else:
                if(prices[idx]<min_price[-1]):
                    min_price.append(prices[idx])
                else:
                    min_price.append(min_price[-1])
            max_price.append(-1)
        # find max in n->0 order
        for idx in range(len(prices)-1,-1,-1):
            if(idx==(len(prices)-1)):
                max_price[idx]=prices[idx]
            else:
                if(prices[idx]>max_price[idx+1]):
                    max_price[idx]=prices[idx]
                else:
                    max_price[idx]=prices[idx+1] 
        
        max_profit = 0
        print(max_price)
        print(min_price)
        for idx in range(0,len(prices)):
            profit=max_price[idx]-min_price[idx]
            if(profit>max_profit):
                max_profit=profit
        return max_profit
            

        