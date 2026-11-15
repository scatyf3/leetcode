class Bucket:
    __slots__ = ("cnt", "keys", "prev", "next")

    def __init__(self, cnt=0):
        self.cnt = cnt
        self.keys = set()
        self.prev = self.next = None

    def __repr__(self):
        return f"{self.cnt}:{self.keys}"


class AllOne:
    def __init__(self):
        self.bucket_of = {}          # key -> 所在的桶
        self.head = Bucket(0)        # cnt=0 的虚拟桶: 不存在的 key 视为在这里, keys 永远为空
        self.tail = Bucket(0)
        self.head.next, self.tail.prev = self.tail, self.head

    def __repr__(self):
        parts, node = [], self.head.next
        while node is not self.tail:
            parts.append(repr(node))
            node = node.next
        return " <-> ".join(parts)

    # ---------- 链表原语 ----------
    def _insert_after(self, node, cnt):
        new = Bucket(cnt)
        new.prev, new.next = node, node.next
        node.next.prev = new
        node.next = new
        return new

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _bucket_between(self, left, right, cnt):
        """返回 left/right 之间 cnt 对应的桶, 没有就新建"""
        if left.cnt == cnt:
            return left
        if right.cnt == cnt:
            return right
        return self._insert_after(left, cnt)

    # ---------- 核心: 把 key 从 src 挪到 dst_cnt ----------
    def _move(self, key, src, dst_cnt):
        # 1. 先找/建目标桶 (必须在摘掉 src 之前, 新桶以 src 为锚点)
        if dst_cnt > 0:
            left, right = (src, src.next) if dst_cnt > src.cnt else (src.prev, src)
            dst = self._bucket_between(left, right, dst_cnt)
            dst.keys.add(key)
            self.bucket_of[key] = dst
        else:                        # 减到 0 = 回到 head, 即删除
            del self.bucket_of[key]
        # 2. 离开 src
        if src is not self.head:
            src.keys.remove(key)
            if not src.keys:
                self._unlink(src)

    # ---------- 对外接口 ----------
    def inc(self, key: str) -> None:
        src = self.bucket_of.get(key, self.head)
        self._move(key, src, src.cnt + 1)

    def dec(self, key: str) -> None:
        src = self.bucket_of[key]
        self._move(key, src, src.cnt - 1)

    def getMaxKey(self) -> str:
        return next(iter(self.tail.prev.keys), "")   # 空时 tail.prev 是 head, keys 为空

    def getMinKey(self) -> str:
        return next(iter(self.head.next.keys), "")   # 空时 head.next 是 tail, keys 为空
