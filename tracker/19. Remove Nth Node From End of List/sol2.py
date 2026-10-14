# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        '''
        一趟扫描. 双指针的"提前量"母题: 让 fast 先走 n 步, 之后同步走到 fast 到末尾,
        slow 就停在倒数第 n+1 个 —— 也就是待删节点的前驱.

        推导: 目标是 idx L-n, 删它需要 slow 停在 idx L-n-1.
              fast 先走 k 步, 同步到 fast 抵达 idx L-1 时 slow 在 idx L-1-k.
              令 L-1-k == L-n-1  =>  k == n.

        删头 (n == L) 时前驱是 idx -1, 不存在 —— dummy 就是那个 idx -1.
        这是"头可能被删/被换就上哨兵"的标准场景, 见 notes/linked-list-template.md.
        '''
        dummy = ListNode(0, head)
        slow = fast = dummy

        # 精确走 n 步. 用 range 而不是 `while ... and i < n`:
        # 后者会把"走不满 n 步"静默吞掉, 变成落点偏一格; range 走不满会当场崩.
        # 有 dummy 之后总长 L+1 > n, 一定走得满.
        for _ in range(n):
            fast = fast.next

        # fast 停在最后一个节点时, slow 停在待删节点的前驱
        while fast.next:
            fast = fast.next
            slow = slow.next

        slow.next = slow.next.next
        return dummy.next          # 不是 head: 头被删掉时 head 已经是野的

        '''
        Dry Run (L=5, n=2, 目标是 4):
            dummy->1->2->3->4->5
            走 n 步 : fast=2
            同步走   : fast=5(末尾) 时 slow=3
            删       : 3.next = 5
        Test Cases: L=1..29 的全部 (L, n) 组合对拍通过
        '''
