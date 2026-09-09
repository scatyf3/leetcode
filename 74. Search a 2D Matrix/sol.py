class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        '''
        one row: [l,r]
        first iterate throught earch rows bound, than
        or even in c++, just naive binary regradless of stride
        '''
        inner_len = len(matrix[0])
        which_inner_list = -1
        outer_len=len(matrix)
        l=0
        r=outer_len-1
        mid = int((l+r)/2)
        while(l<=r):
            if matrix[mid][0]<=target and matrix[mid][inner_len-1]>=target:
                which_inner_list=mid
                break
            elif matrix[mid][0]>target:
                r=mid-1
            elif  matrix[mid][inner_len-1]<target:
                l=mid+1
            mid = int((l+r)/2)
        '''
        print(which_inner_list)
        0 for eg1, 1 for eg2
        print and debug is good
        '''
        if which_inner_list==-1:
            return False
        l=0
        r=inner_len-1
        mid = int((l+r)/2)
        inner_list=matrix[which_inner_list]
        while(l<=r):
            if inner_list[mid]==target:
                return True
            elif inner_list[mid]>target:
                r=mid-1
            else:
                l=mid+1
            mid = int((l+r)/2)
        return False
