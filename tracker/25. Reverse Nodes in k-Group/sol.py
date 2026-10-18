# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseKGroup(self, head: ListNode | None, k: int) -> ListNode | None:
        def reverse(curr):
            # 只管链内：把以 None 结尾的整段反过来 (就是 206)
            prev = None
            while curr:
                nxt = curr.next
                curr.next = prev
                prev = curr
                curr = nxt

        def show(n):
            # debug: 打印一段链, 限 20 个防成环死循环
            s = []
            while n and len(s) < 20:
                s.append(n.val)
                n = n.next
            print(s)

        # 每组要接 2 根线: before → last, first → after, 所以手里要有 4 个 node
        # before, last 是找的; first, after 要在动指针前先存
        dummy = ListNode()
        dummy.next = head
        before = dummy
        while True:
            last = before
            for _ in range(k):
                last = last.next          # 先走再判空
                if last is None:
                    return dummy.next
            first = before.next
            after = last.next

            last.next = None              # 剪下来
            reverse(first)                # 翻转
            # show(last)                  # debug: 这一组翻完, 应为 [k..1]
            before.next = last            # 接回去
            first.next = after
            # show(dummy.next)            # debug: 整条链

            before = first                # first 现在是尾, 成为下一组的 before
