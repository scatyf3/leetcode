# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        '''
        递归版: 先递到底,回溯的路上翻转(后序)
        O(n) 时间 / O(n) 空间(栈深度)
        '''
        if head is None or head.next is None:
            return head              # 空表或只剩一个,它自己就是新头
        p = self.reverseList(head.next)  # 先把后半截整个翻好,p 是新头
        # 此刻 head.next 还指着后半截翻转后的**尾巴**,所以能一步接回来
        head.next.next = head        # 让那个尾巴指向自己
        head.next = None             # 断开旧的正向指针,否则成环
        return p                     # 新头原样往上传,全程不变


# 另一种递归写法: 尾递归,翻转在递下去的路上做
# 本质就是 sol.py 那个循环换了层皮,dfs 的两个参数 = 循环里的 prev/curr
# 迁移性不如上面那版(25. Reverse Nodes in k-Group 用不上)
#
# class Solution:
#     def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
#         def dfs(prev, curr):
#             if curr is None:      # 走到尽头,prev 就是新头
#                 return prev
#             nxt = curr.next       # 存住去路
#             curr.next = prev      # 掉头
#             return dfs(curr, nxt)
#         return dfs(None, head)
