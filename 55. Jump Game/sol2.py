def canJump(self, nums):
    max_reach = 0          # 目前能到达的最远下标
    for i, x in enumerate(nums):
        if i > max_reach:  # 走不到 i 了，后面全断
            return False
        max_reach = max(max_reach, i + x)
        # 想想：这里能不能提前 return True？
    return True

'''

如果 dp 永远是 [T,T,...,T,F,F,...,F]（前缀全 True，后面全 False），那这个长度 n 的数组其实只携带了一个数的信息。是哪个数？

一旦你只维护那个数，内层那个 for j 循环就没必要了——它只是在把一堆已经是 True 的格子反复写成 True。
'''
