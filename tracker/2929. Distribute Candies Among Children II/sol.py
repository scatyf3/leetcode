class Solution:
    def distributeCandies(self, n: int, limit: int) -> int:
        cnt=0
        #minimal=max((n-2)//3,0) # ceil
        #print(minimal)
        #res=[]
        #cur=[]
        def dfs(cand,remain):
            nonlocal cnt
            # nonlocal minimal
            # print(cand,remain)
            if cand<0:
                return
            if remain==0 and cand==0:
                cnt+=1
                #res.append(cur[:])
            for i in range(0,min(remain+1,limit+1)):
                #cur.append(i)
                dfs(cand-1,remain-i)
                #cur.pop()
        dfs(3,n)
        #print(res)
        return cnt