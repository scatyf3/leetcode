Design 类：先列每个 API 读写哪些状态。`tweets: userId → list[(time, tweetId)]`（发推天然按时间追加），`follows: userId → set`（unfollow 用 `discard`），全局自增 `time`。

最难的 `getNewsFeed` = **合并 k 个有序列表**：自己 + 每个关注者的最新一条入堆，弹 10 次，弹出谁就补谁的下一条。全量入堆也能 AC，只是慢。

⚠ 自己的推文要算；tweetId 不代表时间。
