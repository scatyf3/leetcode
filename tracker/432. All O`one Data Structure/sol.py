from collections import defaultdict

class AllOne:

    def __init__(self):
        self.cnt = {}                       # key -> 次数
        self.bucket = defaultdict(set)      # 次数 -> 这个次数的 key；空桶一律删掉
        self.mn = self.mx = 0               # 当前最小 / 最大次数，0 = 空

    def inc(self, key: str) -> None:
        c = self.cnt.get(key, 0)
        self.cnt[key] = c + 1
        self.bucket[c + 1].add(key)
        if c == 0:
            self.mn = 1                     # 新 key 次数是 1，一定是最小
        else:
            self.bucket[c].discard(key)
            if not self.bucket[c]:
                del self.bucket[c]
                if self.mn == c:            # 最小桶空了，那个 key 刚去了 c+1
                    self.mn = c + 1
        self.mx = max(self.mx, c + 1)

    def dec(self, key: str) -> None:
        c = self.cnt[key]
        self.bucket[c].discard(key)
        emptied = not self.bucket[c]
        if emptied:
            del self.bucket[c]
        if c > 1:
            self.cnt[key] = c - 1
            self.bucket[c - 1].add(key)
            self.mn = min(self.mn, c - 1)
            if emptied and self.mx == c:    # 最大桶空了，那个 key 刚去了 c-1
                self.mx = c - 1
            return
        # c == 1：key 直接移除
        del self.cnt[key]
        if not self.cnt:
            self.mn = self.mx = 0
        elif emptied:                       # 次数 1 的全没了，最小值往上找 ← 唯一不是 O(1) 的地方
            m = 2
            while m not in self.bucket:
                m += 1
            self.mn = m

    def getMaxKey(self) -> str:
        return next(iter(self.bucket[self.mx])) if self.mx else ""

    def getMinKey(self) -> str:
        return next(iter(self.bucket[self.mn])) if self.mn else ""