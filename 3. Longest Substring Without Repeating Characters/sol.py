class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}
        l = best = 0
        for r, c in enumerate(s): # index, elem
            if c in last and last[c] >= l: # invalid sliding windows
            # 居然可以直接判断一个key是否in dict
                l = last[c] + 1 # move left 
            last[c] = r # record current char's last seen pos
            if r - l + 1 > best: # max
                best = r - l + 1
        return best


'''
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        # greedy: one local optimal must contain in other larger optimal, eg "a" in "ab" in "abc"
        # greedy with order, ab can in "abc" or "cab"
        # sliding windows
        # 我这里对swa的理解错误，字面意义上swa而不是错了就l=r
        l=0
        r=0
        n=len(s)
        st=set()
        couter=0
        max_len=0
        while(r<n):
            # print(st)
            # print(s[r])
            if s[r] in st:
                st.remove(s[l])
                l+=1
                # st=st.clear() # wrong
                # print(st)
                max_len=max(couter,max_len)
                couter-=1
            else:
                st.add(s[r])
                couter+=1
                r+=1
        max_len=max(couter,max_len) # update while end the loop instead of encouter duplicate str
        return max_len

'''
