class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        mp = {}
        cur_node=head
        if head is None:
            return None
        while cur_node:
            cur_node_new = Node(cur_node.val,None)
            mp[cur_node]=cur_node_new
            cur_node=cur_node.next
        cur_node=head
        while cur_node:
            cur_node_new=mp[cur_node]
            if cur_node.next is not None:
                cur_node_new.next=mp[cur_node.next]
            if cur_node.random is not None:
                cur_node_new.random=mp[cur_node.random]
            cur_node=cur_node.next
        return mp[head]


        