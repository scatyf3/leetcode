class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        st = set(nums)
        starts = []
        for elem in st:
            if elem-1 not in st:
                starts.append(elem)
        longest = 0
        
        for start in starts:
            cur_len=1
            while start+1 in st:
                cur_len+=1
                start+=1
            longest=max(cur_len,longest)
        return longest
