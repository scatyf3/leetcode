class Solution:
    def isValid(self, s: str) -> bool:
        '''
        Input: s, 只含 "()[]{}" 六种字符
        Target: 判断括号是否合法配对
        Return: bool

        栈的不变式:stk 里装的是"已经开启、但还没闭合的左括号",栈顶是最近开启的那个。
        右括号只能和栈顶配 —— 括号的嵌套是后进先出,这就是为什么用栈。
        '''
        # 反向映射:右 -> 左。
        # 键的方向由"查表那一刻手上拿着什么"决定 —— 进 else 分支时 c 一定是右括号,
        # 所以必须以右括号为键。写成 {"(" : ")"} 会 KeyError。
        vaild_pair = {")":"(","]":"[","}":"{"}
        left = {"(","[","{"}
        right = {")","]","}"}
        stk = []
        for c in s:
            if c in left:
                stk.append(c)
            else:
                if len(stk)==0:              # 栈空却来了右括号,无处可配
                    return False
                if stk[-1]!=vaild_pair[c]:   # 栈顶不是它对应的左括号 -> 类型错配
                    return False
                else:
                    stk.pop()                # 配上了,这一对结清
        # 收尾 edge case:循环结束 != 答案成立。
        # 还有左括号压在栈里说明它们从没被闭合,例如 "(" 、"((" 、"([" 。
        if len(stk)!=0:
            return False
        return True

        '''
        Dry Run: s = "([)]"
        ( -> push      stk=['(']
        [ -> push      stk=['(','[']
        ) -> 栈顶'[' != vaild_pair[')']='('  -> False   (嵌套交叉,正确拒绝)

        Test Cases:
        "()"      -> True
        "()[]{}"  -> True
        "{[]}"    -> True
        "(]"      -> False   类型错配
        "([)]"    -> False   嵌套交叉
        "]"       -> False   栈空时来了右括号
        "("       -> False   末尾栈非空  <- 收尾检查专门管这个
        "(("      -> False   同上
        ""        -> True    空串合法,栈从头到尾是空的
        '''
