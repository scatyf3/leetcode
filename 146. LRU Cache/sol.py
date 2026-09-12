class LRUCache:

    def append_head(self,key,value):
        new_node = Node(key,value)
        cur_next=self.head.next
        # update head
        self.head.next=new_node
        # update cur_next
        if cur_next is not None:
            cur_next.prev=new_node
        # update new node
        new_node.prev=self.head
        new_node.next=cur_next
        # update map
        self.mp[key]=new_node

    def remove_tail(self):
        tail_node = self.tail.prev
        if tail_node.key!=-1:
            del self.mp[tail_node.key]
        tail_node.prev.next = self.tail # ← 补: 正向链也要绕过被删的节点
        self.tail.prev = tail_node.prev # move tail head 1 step
        tail_node.prev = None # move tail node prev to None



    def update_to_head(self,key):
        # search a node and remove
        node=self.mp[key]
        prev_node=node.prev
        next_node=node.next
        # connect prev and next
        if prev_node is not None:
            prev_node.next=next_node
        if next_node is not None:
            next_node.prev=prev_node

        # append to head
        prev_head=self.head.next
        # update head
        self.head.next=node
        # update new node
        node.prev=self.head
        node.next=prev_head
        prev_head.prev=node # ← 补: 老的第一个节点要回指过来, 否则反向链断




    def __init__(self, capacity: int):
        self.mp = {}
        self.head=Node(-1,-1)
        self.tail=Node(-1,-1)
        self.capacity=capacity
        self.size=0
        self.head.next=self.tail
        self.tail.prev=self.head

    def get(self, key: int) -> int:
        if key not in self.mp:
            return -1
        val = self.mp[key].val
        # move to head
        self.update_to_head(key)
        return val

    def put(self, key: int, value: int) -> None:
        # ← 补: key 已存在时只更新 val + 挪到队头, 不能再建一个节点
        #        (否则旧节点留在链表里, 被淘汰时会把新节点的 mp 项删掉)
        if key in self.mp:
            self.mp[key].val=value
            self.update_to_head(key)
            return
        self.append_head(key,value)
        self.size+=1
        if self.size>self.capacity:
            self.remove_tail()
            self.size-=1





class Node:
    def __init__(self,key:int, val: int):
        self.key=key
        self.val=val
        self.prev=None
        self.next=None
