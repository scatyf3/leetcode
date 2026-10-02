# 131. Palindrome Partitioning

1. 思考的起点就不对，我思考的是从1-slice开始，然后merge，但是这样复杂性太高了
2. iterate through s，然后切valid的prefix切片，迭代完了结算；不能迭代一半结算，否则suffix不valid
