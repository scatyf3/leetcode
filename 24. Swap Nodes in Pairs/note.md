# 24. Swap Nodes in Pairs

比想象中的难。

## iteration

1. 迭代，每一步交换: prev → cur → nxt → nxt_nxt  变成  prev → nxt → cur → nxt_nxt
2. 4 windows，每次反转cur/next
3. 纯reverse好像反转prev和cur，这里变量语义不一样