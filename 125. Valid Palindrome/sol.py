class Solution:
    def isPalindrome(self, s: str) -> bool:
        '''
        c.isalnum()   # 是字母或数字吗
        c.isalpha()   # 是字母吗
        c.isdigit()   # 是数字吗
        '''
        
        s = s.lower() # 大小写，lower upper；str不让修改只能覆盖
        slst = [c for c in s if c.isalpha()] # 同理，不能修改，开list逐元素处理
        s = "".join(slst) # 然后join到一起 
        l=0
        r=len(s)-1
        while(l<=r):
            if s[l]!=s[r]:
                return False
            l+=1
            r-=1
        
        return True
        