class Solution:
    def numOfWays(self, nums: List[int]) -> int:
        MOD = 10**9 + 7
        n = len(nums)

        # 1. 杨辉三角预处理：comb[a][b] = C(a, b) mod MOD
        comb = [[0] * (n + 1) for _ in range(n + 1)]
        for a in range(n + 1):
            comb[a][0] = 1
            for b in range(1, a + 1):
                # 选本元素+不选本元素
                comb[a][b] = (comb[a-1][b]+ comb[a-1][b-1]) % MOD

        # 2. ways(arr) = 能建出 arr 这棵 BST 的排列数
        def ways(arr):
            if len(arr)==0:                                # base case
                return 1
            root = arr[0]
            left  = [x for x in arr if x<root]        # 左组
            right = [x for x in arr if x>root]        # 右组
            return comb[len(arr)-1][len(left)] * ways(left) * ways(right)  % MOD  # C(L+R, L) · 左 · 右

        # 3. 减掉原数组本身
        return (ways(nums) - 1) % MOD
