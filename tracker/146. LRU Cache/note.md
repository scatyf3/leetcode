# 146. LRU Cache

## pass4

我觉得这类数据结构做对需要良好的设计
1. node，如果有额外的复杂linkedlist类，需要`__repr__`打印出结果
2. 封装三个helper function，这样便于debug一些功能，以及保证主逻辑顺畅
3. size和capacity的处理

## pass3
1. 处理size在哪里增减，处理node有无在hash里的俩情况
2. 断双向链表2步，连双向链表4步

## pass 2

1. 双向链表我们用最傻的办法，node，然后显式获得prev_node 和 next_node，然后直接操作，我们需要处理两个方向四个link
2. 怎么删除hash table里的pair？ `del self.map[queue_tail.key]` 

## pass 1
key idea知道，但是linkeded list小操作不熟悉，一口气写不对，有无linkededlist的小操作题目练习？