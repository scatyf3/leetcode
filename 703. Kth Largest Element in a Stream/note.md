# 703. Kth Largest Element in a Stream

1. 维护一个k heap，维护的是「最大的topk value」，但是是最小堆，堆顶即我们想找的元素
2. 为了保持这个性质，for each incoming elem，若其大于堆顶，pop - push，else不管
3. add之后res比较烦，可能是当前val，可能是堆顶，写一下分类讨论