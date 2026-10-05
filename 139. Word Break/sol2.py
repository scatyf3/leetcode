class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        '''
        用dp试一下，这里的含义是，每个slices都迭代能不能被wordDict里组合出来
        s = "leetcode"
        dp FFFTFFFT

        s="catsandog"
        dp=FFTTFFTFF

        递推是 prefix能否被组成，和当前的切片能否被组成
        '''
        dp=[True]+[False for _ in range(len(s))]
        for i in range(1,len(s)+1):
            for word in wordDict:
                len_w = len(word)
                prefix_index_end = i-len_w
                cur_slice=s[prefix_index_end:i]
                if prefix_index_end>=0:
                    dp[i] = dp[i] or (cur_slice==word and dp[prefix_index_end])
        return dp[-1]
