class TimeMap:

    def __init__(self):
        self.times = {}   # key -> [t1, t2, ...]  题目保证 set 的 timestamp 严格递增，append 即有序
        self.vals = {}    # key -> [v1, v2, ...]  和 times 下标一一对应

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.times.setdefault(key, []).append(timestamp)
        self.vals.setdefault(key, []).append(value)

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.times:
            return ""
        times = self.times[key]
        l, r = 0, len(times) - 1
        while l <= r:
            mid = (l + r) // 2
            if times[mid] <= timestamp:   # P(mid) = T
                l = mid + 1
            else:
                r = mid - 1
        # 退出: [0..r] 全 T, [l..] 全 F → r = 最后一个 <= timestamp
        return self.vals[key][r] if r >= 0 else ""

        

'''
store (key,value,timestamp)
given a key, return nearest(according to timestamp) value 

hashmap key => (some storage related to timestamp and value)

key => (timestamp => value)

first intuition: 
stack, but no time seq

hashmap timestamp => value, use binary search

TimeMap timeMap = new TimeMap();
timeMap.set("foo", "bar", 1);  // store the key "foo" and value "bar" along with timestamp = 1.
timeMap.get("foo", 1);         // return "bar"
timeMap.get("foo", 3);         // return "bar", since there is no value corresponding to foo at timestamp 3 and timestamp 2, then the only value is at timestamp 1 is "bar".
timeMap.set("foo", "bar2", 4); // store the key "foo" and value "bar2" along with timestamp = 4., foo is updated
timeMap.get("foo", 4);         // return "bar2"
timeMap.get("foo", 5);         // return "bar2"
'''