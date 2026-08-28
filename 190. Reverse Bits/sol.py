class Solution:
    def reverseBits(self, n: int) -> int:
        '''
        Input: n, 32 位无符号整数
        Target: 把这 32 位首尾颠倒
        Return: 反转后的整数

        思路: n to binary -> 从末尾往前读 -> to int

        唯一的坑:位宽恒为 32,不是 len(bin(n))。前导零也是有效位,
        反转后它们全跑到低位去,位置信息一个都不能丢。
        n=1 -> 000...001 反转成 100...000 = 2**31,不是 1。
        '''
        BITS = 32
        bits = f"{n:0{BITS}b}"          # n to binary,补足 32 位

        new_bits = []
        for i in range(len(bits) - 1, -1, -1):   # 从末尾往前读,append 天然从 0 往后写
            new_bits.append(bits[i])

        return int("".join(new_bits), 2)         # to int

        '''
        f-string 的 0{BITS}b 三段读:
            0      不够宽时用零填充(不写就是空格填充)
            {BITS} 目标宽度,嵌套花括号会先求值成 32,所以 "32" 全文只出现一次
            b      按 binary 输出
        比 bin(n)[2:].zfill(32) 少两步:它一开始就不产生 '0b' 前缀,所以不用切;
        补零是格式化自带的。

        range(len(bits)-1, -1, -1) 三个参数 = 起点、终点(取不到)、步长。
        想走到下标 0,终点必须写 -1 而不是 0,否则漏掉最后一位 —— 倒序 range
        最经典的 off-by-one。

        Dry Run: n = 1
        f"{1:032b}"  -> "00000000000000000000000000000001"
        倒着 append  -> "10000000000000000000000000000000"
        int(...,2)   -> 2147483648

        Test Cases:
        43261596   -> 964176192
        4294967293 -> 3221225471
        1          -> 2147483648
        2147483648 -> 1
        0          -> 0
        4294967295 -> 4294967295   全 1,反转还是自己
        '''
