贪心维护 `max_reach` = 目前能到的最远下标：扫到 i 时若 `i > max_reach` 就断了返回 False，否则 `max_reach = max(max_reach, i + nums[i])`，扫完返回 True。

⚠ 第一版是 `dp[i]` = 能否到达 i 的布尔数组，内层逐格标 True，O(n²)；但 dp 永远是 T…T F…F 前缀，只携带一个数 —— 就是 `max_reach`。
