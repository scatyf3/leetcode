class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        '''
        subarray sum只能转换为两个prefix之差
        我们迭代nums，获得当前prefix sum，我们反搜 value是 k-prefix_sum 的在不在它前面，在不在set里
        hashmap: prefix sum - [prefix_end_index] （cnt)
        pre[i]-pre[j]==k
        '''
        prefix_sum_counter = Counter()
        prefix_sum_counter[0]=1 #initial state
        prefix_sum = 0
        res = 0
        for elem in nums:
            # pre[i]-pre[j]=k
            prefix_sum+=elem
            if (prefix_sum-k) in prefix_sum_counter:
                res+=prefix_sum_counter[prefix_sum-k]
            prefix_sum_counter[prefix_sum]+=1
        return res