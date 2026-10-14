# ✗ 错误版本, 留作对照. 正确版见 sol2.py
#
# 双指针的主干是对的(提前量 = n), 1 < n < L 的用例全过, 错在两个边界:
#
#   L  n | 期望         | 实际
#   3  1 | [1,2]        | []            <- Bug A
#   3  2 | [1,3]        | [1,3]   ok
#   3  3 | [2,3]        | [1,3]         <- Bug B
#   5  1 | [1,2,3,4]    | []            <- Bug A
#   5  5 | [2,3,4,5]    | [1,3,4,5]     <- Bug B
#
# Bug A: `if n == 1: return None` 说的是"删倒数第1个 => 链表变空", 只有 L==1 才成立.
#        想挡的是"链表只剩一个节点", 判据却写成了 n. 所有 n==1 的用例都被它吃掉.
#
# Bug B: `while fast.next is not None and i < n` 把"还能走"和"走够了"混在一个条件里.
#        n == L 时 fast 最多到最后一个节点(idx L-1), i 停在 L-1 = n-1, 少走一步就
#        静默退出; 第二个 while 一次不跑, slow 还在 head, 于是删掉了第 2 个节点.
#
#        为什么必须精确走 n 步: 目标是 idx L-n, 要删它 slow 得停在 idx L-n-1.
#        fast 先走 k 步, 同步到 fast 抵达 idx L-1 时 slow 在 idx L-1-k,
#        令 L-1-k == L-n-1 => k == n.
#        而删头时 L-n-1 == -1, 那个前驱节点根本不存在 —— 这就是 dummy 的位置.


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        fast = head
        head_backup = head
        i = 0
        if n == 1:
            return None
        while fast.next is not None and i<n:
            fast = fast.next
            i+=1
        while fast.next is not None:
            fast = fast.next
            head = head.next
        head.next=head.next.next
        return head_backup
