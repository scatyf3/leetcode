class Solution:
    def hammingWeight(self, n: int) -> int:
        '''
        Brian Kernighan 算法:n &= n - 1 每次**恰好消掉最低位的那个 1**。
        循环次数 = 1 的个数,而不是 32 —— 稀疏的数(如 128)只转 1 轮。

        为什么 n & (n-1) 能消掉最低位的 1:
            n     = ...a 1 0000     (最低位的 1 后面跟着 k 个 0)
            n-1   = ...a 0 1111     (借位:那个 1 变 0,后面的 0 全变 1)
            n&(n-1)=...a 0 0000     (高位不变,最低位的 1 被清掉)
        '''
        counter = 0
        while n:
            n &= n - 1
            counter += 1
        return counter

        '''
        对比 190 的位运算版:那里必须 for _ in range(32) 固定轮数,因为要处理每一位;
        这里 while n 反而是对的,因为只关心 1 的个数,n 归零就是数完了。
        同样是位运算,循环条件的选择取决于"零位算不算数"。

        Dry Run: n = 12 (1100)
        1100 & 1011 = 1000   counter=1
        1000 & 0111 = 0000   counter=2
        n=0 退出 => 2
        '''
