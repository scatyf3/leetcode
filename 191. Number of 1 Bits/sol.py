class Solution:
    def hammingWeight(self, n: int) -> int:
        '''
        Input: n, 正整数
        Target: 数出二进制里有多少个 1(汉明重量)
        Return: int

        和 190 不同,这题**不需要**补足 32 位:前导零不贡献任何 1,
        补不补结果一样。190 必须补是因为反转会改变每一位的位置。
        '''
        counter=0
        bits = f"{n:0b}"          # 二进制串,不带 '0b' 前缀
        for c in bits:            # 只要值不要下标 -> 直接遍历字符
            if c=='1':
                counter+=1
        return counter

        '''
        f"{n:0b}" 里的 0 是"零填充"标志,但后面没给宽度,所以实际不填充,
        等价于 f"{n:b}"。想补足 32 位才写 f"{n:032b}"(见 190)。

        更短的等价写法:
            return f"{n:b}".count('1')
            return bin(n).count('1')     # '0b' 前缀里没有 1,不影响计数
            return n.bit_count()         # Python 3.10+

        Dry Run: n = 11
        f"{11:0b}" -> "1011"
        逐字符: 1 ->1, 0 ->1, 1 ->2, 1 ->3
        => 3

        Test Cases:
        11         -> 3     1011
        128        -> 1     10000000
        2147483645 -> 30
        0          -> 0     "0",一个 1 都没有
        1          -> 1
        4294967295 -> 32    全 1
        '''
