class Solution:
    def peakIndexInMountainArray(self, arr: list[int]) -> int:
        # binary search
        l=0
        r=len(arr)-1
        # we care about mid vs mid+1
        # if mid<mid+1, we are in left of peak, else right
        # will end at r(mid) - l(mid+1), l is peak
        while l<=r:
            mid=(l+r)//2
            if arr[mid]<arr[mid+1]:
                l=mid+1
            else:
                r=mid-1
        #print(l,arr[l])
        #print(r,arr[r])
        return r+1 # 

        