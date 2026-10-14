# 25. Reverse Nodes in k-Group

我自己写了个naive版，但感觉非常麻烦，我们用array存一个reverse区间的start和end，内部reverse，外部连线

但是非常非常容易连出环...agent给了个建议的template

### template

1. 还是保存每个group的prev，end，和next group
2. 正常反转，但是prev是下一组的start，让反转后的tail直接连到下一组了
3. 处理head，上一组的tail链接现在组的head，然后update prev

感觉很复杂，这好像也是快慢指针+反转的集大成题目，可以mark下