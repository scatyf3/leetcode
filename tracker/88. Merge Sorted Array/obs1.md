merge两个array：
1. 读写双指针
2. 但是为了方便，我们从后面开始merge，省去从前面merge把元素往后移动的麻烦
3. 怎么写loop？判断read2比较麻烦，否则用write写循环也可以，但是if的条件非常恶心，第一个分支时 `if read_2 < 0 or (read_1 >= 0 and nums1[read_1] > nums2[read_2]):`

