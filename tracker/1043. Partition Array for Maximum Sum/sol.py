class Solution:
    def maxSumAfterPartitioning(self, arr: list[int], k: int) -> int:
        # dp store max sum in current index
        # for each elem, check to cover prev 3
        dp = [0 for i in range(len(arr)+1)]
        for index,elem in enumerate(arr):
            dp_index=index+1
            for subarr_start in range(max(index-k+1,0),index+1):
                dis = index-subarr_start+1
                max_sub_arr = max(arr[subarr_start:index+1])
                # print(arr[index],dis,arr[subarr_start:index+1])
                dp[dp_index]= max(dp[dp_index],dp[subarr_start]+ max_sub_arr * dis)
        # print(dp)
        return dp[len(arr)]
