class SnapshotArray:

    def __init__(self, length: int):
        self.snapshots={}
        self.length=length
        self.snap_id=0
        # snap_id: the total number of times we called snap() minus 1
        # thus 0 times =>snap_id=-1
        for idx in range(length):
            self.snapshots[idx]=[[0,0]] # sorted

    def set(self, index: int, val: int) -> None:
        # set idx to val
        if self.snapshots[index][-1][0]==self.snap_id: 
            # time not change, override
            self.snapshots[index][-1][1]=val
        else:
            self.snapshots[index].append([self.snap_id,val])
        # print(self.snapshots[index])

    def snap(self) -> int:
        # snap
        # takes a snapshot of the array and returns the snap_id: the total number of times we called snap() minus 1.
        # naive: snap_id => lst
        # complex: index - (value,timestamp)
        self.snap_id+=1
        return self.snap_id-1

    def get(self, index: int, snap_id: int) -> int:
        # edge case of snap_id>self.snapid
        # binary search for snap id
        lst = self.snapshots[index]
        # given the snap id, find value
        l=0
        r=len(lst)-1
        while l<=r:
            mid=(l+r)//2
            cur_snap_id=lst[mid][0]
            if cur_snap_id>snap_id:
                r=mid-1
            elif cur_snap_id<snap_id:
                l=mid+1
            else: # find
                return lst[mid][1]
        # print(lst)
        #print(l,r)
        return lst[r][1]

        

