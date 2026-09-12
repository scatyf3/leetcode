class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        curr = head
        node_map = {}
        while curr is not None:
            cur_new = Node(curr.val,None,None)
            node_map[curr]=cur_new
            curr=curr.next
        curr = head
        # print(node_map)
        while curr is not None:
            nxt=curr.next
            rad=curr.random
            if nxt is not None:
                node_map[curr].next=node_map[nxt]
            if rad is not None:
                node_map[curr].random=node_map[rad]
            curr=curr.next
        return node_map[head]
        
'''
1. 按next遍历，然后random存一个set，建立val和next，当random出现的时候，连这个random
2. 或者索性每个node存hash省事，可以方便access前面的node

hash的想法对
前向引用的通用解法是分两趟:

第一趟:只管建节点、填 map,一根指针都不连
第二趟:再走一遍原链表,这时候所有副本都已经存在了,next 和 random 都变成「查表」这一个动作

但细节不对，我们不保证val唯一，所以map只能是源节点到新节点
'''