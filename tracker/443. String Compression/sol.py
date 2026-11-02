class Solution:
    def compress(self, chars: list[str]) -> int:
        res = []
        char_list = []
        for c in chars:
            if len(char_list)>0 and c==char_list[-1]:
                res[-1]+=1
            elif len(char_list)==0:
                char_list.append(c)
                res.append(1)
            else:
                char_list.append(c)
                res.append(1)
        
        # to str
        assert len(char_list)==len(res)
        valid_idx=0
        for idx in range(len(char_list)):
            if res[idx]>1:
                chars[valid_idx]=char_list[idx]
                len_nums=1
                for d in str(res[idx]): # 更好的写法
                    chars[valid_idx + len_nums] = d
                    len_nums += 1
                valid_idx+=len_nums # not 1+len_nums, len_nums考虑了字符的那个1
            else:
                chars[valid_idx]=char_list[idx]
                valid_idx+=1
        return valid_idx

        