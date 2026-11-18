class Solution:
    def superPow(self, a: int, b: list[int]) -> int:
        MOD = 1337

        def fast_pow(base: int, exp: int) -> int:
            result = 1
            base %= MOD
            while exp:
                if exp & 1:                   # 这一位是 1，乘进结果
                    result = result * base % MOD
                base = base * base % MOD      # 底数平方，对应下一位
                exp >>= 1
            return result

        ans = 1
        for digit in b:
            ans = fast_pow(ans, 10) * fast_pow(a, digit) % MOD
        return ans
