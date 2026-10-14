class Bucket:
    def __init__(self, cnt):
        self.cnt = cnt
        self.keys = set()               # 次数都是 cnt 的 key，set 增删 O(1)
        self.prev = self.next = None


class AllOne:

    def __init__(self):
        self.head = Bucket(0)           # 哨兵：head.next 次数最小，tail.prev 次数最大
        self.tail = Bucket(float('inf'))
        self.head.next, self.tail.prev = self.tail, self.head
        self.where = {}                 # key -> 它所在的 Bucket

    # ---- 两个原语：桶的插入 / 删除，指针只在这里写 ----
    def _insert_after(self, node, cnt):
        b = Bucket(cnt)
        b.prev, b.next = node, node.next
        node.next.prev = b
        node.next = b
        return b

    def _remove(self, b):
        b.prev.next = b.next
        b.next.prev = b.prev

    def inc(self, key: str) -> None:
        cur = self.where.get(key, self.head)        # 新 key 当作在次数 0 的 head 里
        nxt = cur.next
        if nxt.cnt != cur.cnt + 1:                  # 次数 +1 的桶还不存在 → 紧挨着 cur 新建
            nxt = self._insert_after(cur, cur.cnt + 1)
        nxt.keys.add(key)
        self.where[key] = nxt
        if cur is not self.head:
            cur.keys.discard(key)
            if not cur.keys:
                self._remove(cur)

    def dec(self, key: str) -> None:
        cur = self.where[key]                       # 题目保证 key 存在
        if cur.cnt == 1:                            # 减到 0：直接移出
            del self.where[key]
        else:
            prv = cur.prev
            if prv.cnt != cur.cnt - 1:              # 次数 -1 的桶不存在 → 紧挨着 cur 前面新建
                prv = self._insert_after(cur.prev, cur.cnt - 1)
            prv.keys.add(key)
            self.where[key] = prv
        cur.keys.discard(key)
        if not cur.keys:
            self._remove(cur)

    def getMaxKey(self) -> str:
        b = self.tail.prev
        return next(iter(b.keys)) if b is not self.head else ""

    def getMinKey(self) -> str:
        b = self.head.next
        return next(iter(b.keys)) if b is not self.tail else ""
