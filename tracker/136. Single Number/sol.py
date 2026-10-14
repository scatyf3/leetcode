class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        st = set()
        for elem in nums:
            if elem not in st:
                st.add(elem)
            elif elem in st:
                st.remove(elem)
        res = list(st)[0]
        return res
        