class TimeMap:

    def __init__(self):
        # 最naive的做法是list of (key,value,timestamp)，但有点傻
        # key=> list of (value,timestamp)
        # set => append new
        # get => binary search for timestamp, get value
        self.mp = {}

    def set(self, key: str, value: str, timestamp: int) -> None:
        if key in self.mp:
            self.mp[key].append((value,timestamp))
        else:
            self.mp[key]=[(value,timestamp)]

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.mp:
            return ""
        lst = self.mp[key]
        l=0
        r=len(lst)-1
        while l<=r:
            mid = (l+r)//2
            if lst[mid][1] < timestamp:
                l=mid+1 # increase mid
            elif lst[mid][1] > timestamp:
                r = mid-1
            else: # ==
                return lst[mid][0]
        # [r,l], where timestamp is inside 
        if r<0: # left boundary
            return ""
        return lst[r][0]


# Your TimeMap object will be instantiated and called as such:
# obj = TimeMap()
# obj.set(key,value,timestamp)
# param_2 = obj.get(key,timestamp)