class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        '''
        maintain a kest minimal heap for topk elem
        that is to say, compare elem with heap top(minial of max topk)
        '''
        h = nums[:k]
        heapq.heapify(h)

        for elem in nums[k:]:
            if elem>h[0]:
                heapq.heappop(h)
                heapq.heappush(h,elem)
        return h[0]