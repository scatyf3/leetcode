class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        total = sum(nums)
        if total % 2 == 1:
            return False
        target = total // 2

        reachable = {0}
        # 用当前的num更新reachable
        for x in nums:
            new = set()
            for s in reachable:
                if s + x <= target:
                    new.add(s+x)
            reachable |= new
        return target in reachable