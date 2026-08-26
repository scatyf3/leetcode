class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if(len(s)!=len(t)):
            return False
        s_d={}
        t_d={}
        for elem in s:
            if elem not in s_d:
                s_d[elem]=1
            else: 
                s_d[elem]+=1
        for elem in t:
            if elem not in t_d:
                t_d[elem]=1
            else: 
                t_d[elem]+=1
        # or for key in s_d
        for key,value in s_d.items():
            if key not in t_d:
                return False
            if value!=t_d[key]:
                return False
        return True
'''
1. how to handle dictionary, key is in or not branch
2. edge case
3. how to iterate throught dictionary
'''
