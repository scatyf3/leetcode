class Solution:
    def distributeCandies(self, n: int, limit: int) -> int:
        def ways(total):              # 3 个人分 total 颗，不设上限
            if total<0:
                return 0
            return (total+2)*(total+1)//2          # 隔板法：C(total+2, 2)

        over = limit+1              # 硬塞给超限的人多少颗
        return (ways(n)
                - 3 * ways(n- over)           # 某 1 个人超限
                + 3 * ways(n- 2 * over)          # 某 2 个人同时超限
                - ways(n - 3 * over)) # 3 个人都超限

