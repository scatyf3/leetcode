class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        # lowest height dominate the Rectangle => increase stack
        stk = []
        res = 0
        for idx,height in enumerate(heights+[0]):
            while stk and heights[stk[-1]]>height: # increase检查大于
                # POP
                prev_index = stk.pop()
                prev_height = heights[prev_index]
                if stk: # 右边界是idx，左边界是pop后的栈顶而不是prev_index
                    size = (idx-stk[-1]-1) * prev_height # 用prev height
                else: 
                    size = idx * prev_height # idx -(-1) - 1
                # print(size)
                # print(idx, size)
                res = max(res,size)
            # append new
            stk.append(idx)
        return res
