# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        '''
        探针型双指针(快慢指针),两个指针语义相同,只差速度。
        有环的话快指针每轮追近慢指针一格,必定相遇;无环的话快指针先走到 None。
        全程不读 .val —— 判环是拓扑性质,和节点装了什么无关。
        O(n) 时间 / O(1) 空间
        '''
        # 不需要特判空表和单节点,循环条件已经覆盖:
        # head=None -> fast is not None 为假; 单节点 -> fast.next is None 为假
        fast = slow = head
        while fast is not None and fast.next is not None:
            fast = fast.next.next   # 先推进,再比较
            slow = slow.next        # 否则起点处 fast is slow 会立刻误报
            if fast is slow:        # 比身份不比值! fast 可能是 None,is 不解引用所以安全
                return True
        return False

        '''
        Dry Run: A(1) -> B(2) -> A   (环)
        用节点名而不是值来记,身份/数值的混淆才不会藏起来
        init : fast=A slow=A
        iter1: fast=A.next.next=A, slow=B    A is B ? 否
        iter2: fast=A,             slow=A    A is A ? 是 => True

        Test Cases:
        None      -> False   (不进循环)
        [1]       -> False   (fast.next is None)
        [1,2]     -> False   (推进后 fast=None,is 不会炸)
        [1,1,1]   -> False   (三个不同节点同值,用 .val 比会误报 True)
        [3,2,0,-4] pos=1 -> True
        '''
