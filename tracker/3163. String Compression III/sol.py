class Solution:
    def compressedString(self, word: str) -> str:
        lst = []
        idx=0
        while idx<len(word):
            windows_cnt = 1
            curr=word[idx]
            for windows_idx in range(idx+1,idx+9):
                if windows_idx>=len(word) or curr!=word[windows_idx]:
                    break
                else:
                    windows_cnt+=1
            idx+=windows_cnt
            lst.append(str(windows_cnt))
            lst.append(curr)
        return "".join(lst)
        