class Solution:
    def reverseWords(self, s: str) -> str:
        # divide s in to list of word
        res=s.split()
        #print(new_s)
        #res = []
        #cur = []
        #for c in s:
        #    if c==" ":
        #        res.append("".join(cur))
        #        cur.clear()
        #    else:
        #        cur.append(c)
        #res.append("".join(cur))
        #cur.clear()
        # print(res)
        # reverse list of word
        l=0
        r=len(res)-1
        #print(res)
        #print(l)
        #print(r)
        while l<=r:
            tmp=res[l]
            res[l]=res[r]
            res[r]=tmp
            #res.swap(l,r)
            l+=1
            r-=1
        # join the result and return
        new_res=[]
        for word in res:
            new_res.append(word)
            new_res.append(" ")
        new_res.pop()
        return "".join(new_res)