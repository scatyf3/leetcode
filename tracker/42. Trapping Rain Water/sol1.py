class Solution:
    def trap(self, height: List[int]) -> int:
        '''
        input: each block's height
        output: how much water it can trap
        h = [0,1,0,2,1,0,1,3,2,1,2,1]
        L = [0,1,1,2,2,2,2,3,3,3,3,3]
        R = [3,3,3,3,3,3,3,3,2,2,2,1]
        d = [3,2,2,1,1,1,1,0,1,1,1,2] => sum=16
        t =  [0,1,0,1,2,1,0,0,1,0,0]
        L and R unchange between 2 idx => has trap
        unchange between 1 idx =>1
        3 idx => 1+2+1

        '''
        n=len(height)
        L=[-1] * n
        R=[-1] * n
        L_max=-1
        R_max=-1
 
        for idx in range(0,n):
            if idx!=0:
                if height[idx]>L_max:
                    L[idx]=height[idx]
                    L_max=height[idx]
                else:
                    L[idx]=L[idx-1]
            else:
                L[0]=height[0]
                L_max=L[0]
        # find R in reverse, n-1 syntax
        for idx in range(n-1,-1,-1):
            if idx!=n-1:
                if height[idx]>R_max:
                    R[idx]=height[idx]
                    R_max=height[idx]
                else:
                    R[idx]=R[idx+1]
            else:
                R[n-1]=height[n-1]
                R_max=R[n-1]
        
        # use L max and R max find water trap
        # trap = min(L[idx],R[idx])-height[idx]
        # print(L)
        # print(R)
        total = 0
        for i in range(n):
            water_level = min(L[i], R[i])
            total += water_level - height[i]

        return total


