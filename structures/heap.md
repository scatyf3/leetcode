# Heap 通用 trick

heap api

```python
push pop heapify
```

本质上也是个list，所以也能遍历和修改其中元素

---

### API 速查

| 操作 | 写法 | 复杂度 |
|---|---|---|
| 建堆 | `heapq.heapify(h)` | O(n)，原地 |
| 插入 | `heapq.heappush(h, x)` | O(log n) |
| 弹堆顶 | `heapq.heappop(h)` | O(log n) |
| 看堆顶 | `h[0]` | O(1)，不弹 |
| 先推再弹 | `heapq.heappushpop(h, x)` | O(log n)，维护大小为 k 的堆时用 |
| 前 k 大 / 小 | `heapq.nlargest(k, it)` / `nsmallest` | O(n log k) |

### 几个坑

- **只有最小堆**：要大根堆就存 `-x`，取出来再取反。
- **元组按字典序比较**：`(-time, tweetId)` 先比时间，平局才比第二个；第二个元素不能比较（比如 ListNode）时，要在中间塞一个唯一的计数器。
- **是 list 所以能遍历、能改，但是**：只有 `h[0]` 保证是最值，其余位置不是有序的；直接改元素会破坏堆性质，改完要重新 `heapify`。堆不支持删除任意元素。

### 堆什么时候常驻、什么时候随用随建

> 候选集合在每次查询里都一样、只做插入和取堆顶 → 常驻堆（703、295、1046）。
> 候选集合随查询参数变，或者要删任意元素 → 只存原始数据，查询时临时建堆（355 的 getNewsFeed，按 userId + 当前关注关系算）。

### 相关题

- 大小为 k 的堆：[215](../215.%20Kth%20Largest%20Element%20in%20an%20Array/)、[703](../703.%20Kth%20Largest%20Element%20in%20a%20Stream/)、[973](../973.%20K%20Closest%20Points%20to%20Origin/)、[347](../347.%20Top%20K%20Frequent%20Elements/)
- k 路归并：[23](../23.%20Merge%20k%20Sorted%20Lists/)、[355](../355.%20Design%20Twitter/)
- 双堆：[295](../295.%20Find%20Median%20from%20Data%20Stream/)
- 贪心取最大：[1046](../1046.%20Last%20Stone%20Weight/)、[621](../621.%20Task%20Scheduler/)
