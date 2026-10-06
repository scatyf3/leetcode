class Solution:
    def swapPairs(self, head: ListNode | None) -> ListNode | None:
        dummy = ListNode(0, head)
        prev, cur = dummy, head
        # 用迭代需要四个
        while cur and cur.next:
            nxt = cur.next
            nxt_nxt = nxt.next
            # 交换: prev → cur → nxt → nxt_nxt  变成  prev → nxt → cur → nxt_nxt
            prev.next = nxt        # 接进来
            nxt.next = cur         # 对内反向
            cur.next = nxt_nxt     # 接出去
            # 下一对: 交换后 cur 是这一对的尾巴
            prev = cur
            cur = nxt_nxt
        return dummy.next