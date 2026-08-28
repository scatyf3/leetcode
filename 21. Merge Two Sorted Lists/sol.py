# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        '''
        Input: list1, list2 —— 两条各自非递减的链表
        Target: 合并成一条非递减链表
        Return: 新链表的头

        载荷题:要读 .val 比大小(对比 141/206 那类纯拓扑题)。
        哨兵 head 的作用是消灭"结果链表还是空的、第一个节点特殊处理"这个特例,
        全程只有 iterate_node.next = ... 一种写法,最后 return head.next。
        '''
        head = ListNode(-114,None)   # 哨兵,值随便取,只用它的 next
        iterate_node = head          # 分界口:已合并部分的尾巴
        while list1 is not None and list2 is not None:
            if list1.val>list2.val:
                # merge list 2 first
                iterate_node.next = ListNode(list2.val,None)
                list2=list2.next
            else:
                # 相等时取 list1 -> 稳定,相同值保持 list1 在前
                iterate_node.next = ListNode(list1.val,None)
                list1=list1.next
            iterate_node = iterate_node.next
        # 收尾:必有一条已走空。剩下那条本身就是有序的,整段直接接上,不用逐个搬
        if list1 is not None:
            iterate_node.next=list1
        else:
            iterate_node.next=list2   # 可能是 None,那就正好封口
        return head.next              # 不是 return head —— 哨兵不属于结果

        '''
        Dry Run: list1 = 1->2->4, list2 = 1->3->4
        1 vs 1  -> else 取 list1     结果 1
        2 vs 1  -> if   取 list2     结果 1,1
        2 vs 3  -> else 取 list1     结果 1,1,2
        4 vs 3  -> if   取 list2     结果 1,1,2,3
        4 vs 4  -> else 取 list1     结果 1,1,2,3,4
        list1 空 -> 接上 list2 剩下的 4
        => 1->1->2->3->4->4

        Test Cases:
        [] , []      -> []      循环不进,list1 是 None 走 else,接上 list2=None
        [] , [0]     -> [0]
        [0], []      -> [0]
        [1,2,4],[1,3,4] -> [1,1,2,3,4,4]
        [5],[1,2,3]  -> [1,2,3,5]   收尾接的是 list1
        '''
