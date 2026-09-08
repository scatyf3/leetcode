class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        '''
        answer[i] is the number of days you have to wait after the ith day to get a warmer temperature.
        stack

        if larger than top => pop top
        push after check all stack
        [75,71,69,72,76,73]
        [4, 2, 1, 1, 0, 0]
        push 75
        push 71
        push 69
        72, pop(69),pop(71)
        76 pop 71 
        pop 75
        remain in stack:0
        '''
        stk=[]
        res=[0 for _ in range(len(temperatures))]
        for idx,temp in enumerate(temperatures):
            while len(stk)!=0 and stk[-1][1] < temp:
                prev_idx,prev_temp = stk.pop()
                res[prev_idx] = idx-prev_idx
            stk.append((idx,temp))
        return res
        