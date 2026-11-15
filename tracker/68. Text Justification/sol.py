class Solution:
    def fullJustify(self, words: list[str], maxWidth: int) -> list[str]:
        # at least 1 space between 


        def slice_from(index): # return end index
            cnt = 0
            lst = []
            while index<len(words) and cnt<maxWidth:
                if len(lst)>0:
                    cnt+=1
                    lst.append("#")
                cur_word = words[index]
                lst.append(cur_word)
                cnt+=len(cur_word)
                index+=1
            if cnt>maxWidth: # roll back
                word = lst.pop()
                cnt-= len(word)
                lst.pop()
                index-=1
                cnt-=1
            return index, lst, cnt

        def formating(lst, cnt, is_last): # agent老师给了下formating
            res = lst
            num_space = len(lst)//2
            str_len = cnt-num_space
            if is_last or num_space == 0:            # 左对齐：单词间 1 个空格，右边补齐
                for idx in range(1, len(res), 2):
                    res[idx] = " "
                res.append(" "*(maxWidth-cnt))
            else:
                space_len = maxWidth-str_len
                q, r = divmod(space_len, num_space)  # 每个间隙 q 个，左边 r 个间隙各多 1
                for idx in range(1, len(res), 2):
                    k = idx//2                       # 第 k 个间隙
                    res[idx] = " "*(q + (1 if k < r else 0))
            return "".join(res)
        
        res = []
        index=0
        while index<len(words):
            index, lst, cnt=slice_from(index)
            cur_fmt_str = formating(lst, cnt, index==len(words))
            res.append(cur_fmt_str)

        return res
        