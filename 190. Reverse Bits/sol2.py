class Solution:
    def reverseBits(self, n: int) -> int:
        '''
        位运算版,不借字符串。O(1) 空间。
        每轮:摘 n 的最低位,推到 res 的最低位,res 的旧内容整体往高位顶。
        于是 n 最先吐出的(最低位)被顶到最高位,最后吐出的留在最低位 —— 正好首尾颠倒。
        '''
        res = 0
        for _ in range(32):              # 固定 32 轮,不能写 while n:
            res = (res << 1) | (n & 1)   # res 左移腾出一格,填入 n 的最低位
            n >>= 1                      # n 丢掉刚用过的最低位
        return res

        '''
        为什么不能写 while n:
        n 变成 0 就提前退出了,高位那些零没被处理 —— 等于没补前导零,和
        bin(n)[2:] 不 zfill 是同一个错。边界塞进循环次数里,而不是循环体的 if 里。

        和十进制反转是同一个骨架:
            res = res * 10 + n % 10 ;  n //= 10      十进制
            res = (res << 1) | (n & 1);  n >>= 1     二进制(×2 就是 <<1, %2 就是 &1)
        '''


# 按"转成串、倒着读、再转回来"的原始思路展开的版本(等价,留作对照):
#
# class Solution:
#     def reverseBits(self, n: int) -> int:
#         BITS = 32
#         bits = f"{n:0{BITS}b}"
#         new_bits = []
#         for c in reversed(bits):      # 下标只用来取值 -> 不要下标
#             new_bits.append(c)        # 循环体只是 append -> 其实连循环都不要
#         return int("".join(new_bits), 2)
