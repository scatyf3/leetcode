class Solution:
    def partitionLabels(self, s: str) -> list[int]:
        '''
        each letter appears in at most one part
        naive的办法是搞个26,n的index map，然后根据这个做partition？
        退化为每个字母维护L,R? 然后merge interval
        怎么枚举26字母来着
        hint by agent： 「怎么枚举 26 个字母」：不用去枚举字母表，扫一遍 s 就行。
        '''
        first, last = {},{}
        for index, char in enumerate(s):
            if char not in first:
                first[char]=index
                last[char]=index
            last[char]=index
        print(first)
        print(last)
        lst_interval = []
        for key in first:
            lst_interval.append([first[key],last[key],key])
        lst_interval.sort() # sort by first
        merge_list = []
        for interval in lst_interval:
            if not merge_list or merge_list[-1][1] < interval[0]:
                merge_list.append(interval)
            else:
                merge_list[-1] = [min(merge_list[-1][0],interval[0]),max(merge_list[-1][1],interval[1])]
        # print(merge_list)
        for idx in range(len(merge_list)):
            cur = merge_list[idx][1]-merge_list[idx][0]+1 # [L,R] instead of [L,R)
            merge_list[idx]=cur
        return merge_list
