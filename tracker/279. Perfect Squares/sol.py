class Solution:
    def numSquares(self, n: int) -> int:
        mx = int(sqrt(n))
        print(mx)
        dp = [0 for i in range(0,n+1)]
        for i in range(1,n+1):
            cur_min = i
            for j in range(1,mx+1):
                if i-j*j>=0:
                   cur_min=min(cur_min,1+dp[i-j*j])
            dp[i]=cur_min
        return dp[n]