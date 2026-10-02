# 146. LRU Cache


## pass 2

1. 双向链表我们用最傻的办法，node，然后显式获得prev_node 和 next_node，然后直接操作，我们需要处理两个方向四个link
2. 怎么删除hash table里的pair？ `del self.map[queue_tail.key]` 

## pass 1
key idea知道，但是linkeded list小操作不熟悉，一口气写不对，有无linkededlist的小操作题目练习？