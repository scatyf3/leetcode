class Solution:
    def coinChange(self, coins: list[int], amount: int) -> int:
        # dp[i] = 凑出 i 元的最少硬币数，inf 表示凑不出
        dp = [0] + [float("inf")] * amount
        for coin in coins:  # 完全背包：求的是最少枚数，跟顺序无关，coin 放外层也对
            for i in range(coin, amount + 1):  # 从 coin 开始，i - coin >= 0 天然成立
                dp[i] = min(dp[i], dp[i - coin] + 1)
        return dp[amount] if dp[amount] != float("inf") else -1
