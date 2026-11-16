class Solution:
    def mySqrt(self, x: int) -> int:
        if x < 2:
            return x
        a = x
        def F(z):  return z * z - a
        def dF(z): return 2 * z

        z_prev = float(a)                 # 初值取 a，避开 F'(0)=0
        for _ in range(100):              # 最大迭代次数
            z_new = z_prev - F(z_prev) / dF(z_prev)
            if abs(z_new - z_prev) < 1e-6:   # 步长足够小就停
                break
            z_prev = z_new                # 别忘了更新

        r = int(z_new)
        #while r * r > a:                  # 修正浮点误差
        #    r -= 1
        #while (r + 1) * (r + 1) <= a:
        #    r += 1
        return r
