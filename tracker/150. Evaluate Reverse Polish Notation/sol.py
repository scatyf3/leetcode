class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        '''
        is tokens must valid? we start from only consider it is valid
        '''
        stk=[]
        # ops=[] # 不考虑优先级，按来的顺序即可

        for token in tokens:
            if token=='+':
                num1=int(stk.pop())
                num2=int(stk.pop())
                res = num1+num2
                stk.append(res)
            elif token=='-':
                num1=int(stk.pop())
                num2=int(stk.pop())
                res = num2-num1
                stk.append(res)
            elif token=='*':
                num1=int(stk.pop())
                num2=int(stk.pop())
                res = num1*num2
                stk.append(res)
            elif token=='/':
                num1=int(stk.pop())
                num2=int(stk.pop())
                if num1==0:
                    res=0
                else:
                    res = int(num2/num1)
                    # C/Java 整数除法是截断（-7/2 == -3），Python 的 // 是 floor（-7//2 == -4）
                    # 所以就写 int(num2/num1) 而不要写 //
                stk.append(res)
            else:
                stk.append(token)
        return int(stk[-1])