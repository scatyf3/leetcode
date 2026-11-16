class Solution:
    def myPow(self, x: float, n: int) -> float:
        ans=1
        negative=False
        if n<0:
            n=-n
            negative=True
        while n>0:
            if n&1:
                # mul
                ans*=x
            # step x
            x*=x
            n=n>>1
        if negative: # 不用1/x而是1/ans，减少fp误差
            ans=1/ans
        return ans
'''
13 = 8 + 4 + 1          ← 指数这一层：是加法
x^13 = x^8 · x^4 · x^1   ← 值这一层：变成了乘法
'''
         