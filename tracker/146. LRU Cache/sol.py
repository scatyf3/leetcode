class LRUCache:

    def __init__(self, capacity: int):
        self.hash_table = {}
        self.head = Node(-1,-1)
        self.tail = Node(-1,-1)
        self.capacity = capacity
        self.size = 0
        self.head.next=self.tail
        self.tail.prev=self.head

    def get(self, key: int) -> int:
        if key not in self.hash_table:
            return -1
        node = self._remove_from_lst(key)
        self._insert_head(node)
        # print(self.head)
        return node.value


    def put(self, key: int, value: int) -> None:
        if key not in self.hash_table:
            node = Node(key,value)
            self.size+=1
        else:
            node = self._remove_from_lst(key)
            node.value = value
        self._insert_head(node)
        if self.size>self.capacity:
            self._remove_tail()
            self.size-=1
        # print(self.head)

    # assert node exist
    def _remove_from_lst(self,key) -> Node:
        node = self.hash_table[key]
        node_prev = node.prev
        node_next = node.next
        node_prev.next=node_next # 1 
        node_next.prev=node_prev # 2
        del self.hash_table[key]
        return node

    def _insert_head(self,node):
        head_node = self.head.next
        # 4 link
        head_node.prev=node
        node.next=head_node
        node.prev=self.head
        self.head.next=node
        self.hash_table[node.key]=node

    def _remove_tail(self):
        tail_node = self.tail.prev
        tail_node_prev = tail_node.prev
        tail_node_prev.next=self.tail
        self.tail.prev=tail_node_prev
        del self.hash_table[tail_node.key]

class Node:
    def __init__(self,key,value):
        self.key=key
        self.value=value
        self.prev=None
        self.next=None
    def __repr__(self):
        # print head only for debug
        return f"Node({self.key}, next={self.next})"   # ✗