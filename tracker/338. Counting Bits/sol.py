class Solution:
    def countBits(self, n: int) -> List[int]:
        '''
        Input:
        - n: int, 0 <= n <= 10^5
        Target:
        ans[i] = number of 1's in binary representation of i, for i in [0, n]
        Return: List[int] of length n+1

        递推: i 的二进制 = (i>>1) 的二进制 再接上最低位
              所以 1 的个数 = dp[i>>1] + (最低位是不是 1)
        '''
        dp = [0] * (n + 1)
        for i in range(1, n + 1):
            dp[i] = dp[i >> 1] + (i & 1)
        return dp




class Solution4:
    def countBits(self, n: int) -> List[int]:
        '''
        模拟进位：真的维护一个二进制计数器，从 0 一路 +1 到 n。
        +1 的规则：把末尾连续的一串 1 全部变 0，再把它们前面那个 0 变成 1。
        
        bits 总长只有 log n，所以一步最坏 O(log n)，n 步就是 O(n log n)
        '''
        dp = [0] * (n + 1)
        bits = [0] * (n.bit_length() + 1)  # 低位在前，预留够长就不用判越界
        ones = 0                            # bits 里 1 的个数

        for i in range(1, n + 1):
            j = 0
            while bits[j] == 1:   # 末尾连续的 1 -> 0
                bits[j] = 0
                ones -= 1
                j += 1
            bits[j] = 1           # 它们前面那个 0 -> 1
            ones += 1
            dp[i] = ones

        return dp


class Solution5:
    def countBits(self, n: int) -> List[int]:
        '''
        Solution4 的收缩版：进位规则可以不展开成数组。

        i-1 末尾连续 1 的个数 == i 末尾连续 0 的个数 = trailing_zeros(i)
        （因为进位就是把那串 1 进位成了那串 0）
        而 i & -i 只保留 i 最低位的 1，它的 bit_length()-1 就是 trailing_zeros。

        于是一行：dp[i] = dp[i-1] - trailing_zeros(i) + 1
        '''
        dp = [0] * (n + 1)
        for i in range(1, n + 1):
            tz = (i & -i).bit_length() - 1
            dp[i] = dp[i - 1] - tz + 1
        return dp
