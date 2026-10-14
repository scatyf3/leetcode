# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        '''
        sol.py 的精简版: 同样三步, 但把特判都消掉了.
        对照见 notes/linked-list-template.md

        省掉特判的两个理由:
        - reverse(None) 返回 None, 所以 n<=1 时第 2 步天然是 no-op
        - 切在"左中点"保证 前半 >= 后半, 所以第 3 步只判 second
        '''
        if head is None:
            return

        # 1. split: fast 提前一步起跑 -> slow 停在前半段的最后一个节点(左中点)
        #    循环条件用统一形状 while fast and fast.next, 旋钮只有 fast 的起点:
        #       fast = head       -> slow 落右中点
        #       fast = head.next  -> slow 落左中点(要切断就用这个)
        #    fast 只是配速器, 停在末尾附近, 不是后半段的头
        slow, fast = head, head.next
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next

        # 2. reverse: reverse 已把原 slow.next 的 next 置空, 两半此时已断开;
        #    slow.next=None 是清掉 slow 这侧的指针, 不清会成环. 两句顺序无所谓
        second = self.reverse(slow.next)
        slow.next = None

        # 3. merge
        self.merge_alt(head, second)

    def reverse(self, head):
        '''条件是 curr 不是 curr.next; 返回 prev 不是 curr(curr 恒为 None)'''
        prev, curr = None, head
        while curr is not None:
            nxt = curr.next          # 下一行是破坏性写入, 先抢救
            curr.next = prev
            prev = curr
            curr = nxt
        return prev

    def merge_alt(self, first, second):
        '''
        1,2,3 + 5,4 -> 1,5,2,4,3
        要求 len(first) >= len(second): 于是 second 非空 => first 必非空,
        first 一次都不用判.
        '''
        while second:
            n1, n2 = first.next, second.next   # 两个都先存, 下面两行都会覆盖
            first.next = second
            second.next = n1
            first, second = n1, n2

        '''
        Dry Run (n=5):
            split : 1->2->3 | 4->5      (slow=3, fast=5)
            rev   : 1->2->3 | 5->4
            merge : 1->5->2->4->3
        Test Cases: n = 0..79 全部对拍通过
        '''
