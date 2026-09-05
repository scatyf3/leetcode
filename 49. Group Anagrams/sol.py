class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        '''
        Given an array of strings strs, group the anagrams together.

        is str has repeat str?(problem do not tell us, first assume no repeat)

        def is_anagrams 
            1. sort
            2. str match
        key: sorted str and list(or set to solve repeat)

        convert dict to 2d array
        '''
        dc = {}
        for s in strs:
            s_raw = s
            # s_key = s.sort()
            s_key = key = "".join(sorted(s))
            if s_key not in dc:
                dc[s_key]=[s_raw]
            else:
                dc[s_key].append(s_raw)
        res=[]
        for key in dc:
            res.append(dc[key])
        return res
