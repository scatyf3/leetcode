class Solution:
    def calculate(self, s: str) -> int:
        stack = []
        num = 0
        op = '+'  # num 前面的那个运算符
        for i, c in enumerate(s):
            if c.isdigit():
                num = num * 10 + int(c)
            if c in "+-*/" or i == len(s) - 1:  # num 读完了, 按上一个 op 处理
                if op == '+':
                    stack.append(num)
                elif op == '-':
                    stack.append(-num)
                elif op == '*':
                    num = stack.pop() * num
                    stack.append(num)
                else:
                    tmp = stack.pop()
                    #print(tmp)
                    # print(num)
                    stack.append(int(tmp / num)) # int(/) vs //
                op = c
                num = 0
        return sum(stack)
