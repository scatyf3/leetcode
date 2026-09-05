from typing import List


class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        '''
        Input:
        - board: List[List[str]], 固定 9x9, 每格是 '1'-'9' 或 '.'
        Target: 判断**已填格子**有无违反行/列/宫的"不重复"规则
        Return: bool
        Output: bool

        !! 不是解数独。题面 Note 明说 "could be valid but is not necessarily solvable"
           —— 只查冲突, 不做搜索/回溯。真正解数独是 LC 37 Sudoku Solver。
        !! 合法 != 完整。不要求每行填满 1-9; 一行只有一个 '5' 其余全空也是合法的。

        解法: 朴素三段循环 —— 分别遍历 9 行 / 9 列 / 9 宫, 每组内部查重
        O(1) 时间 / O(1) 空间 (棋盘固定 81 格, 严格说是常数)

        这版逻辑正确, 面试写它能过。缺点纯粹是**代码组织**:
        三段互不相干的循环, 且查宫那段要 4 层嵌套 —— 因为为了"访问一个宫的 9 格",
        你被迫写出遍历它的代码。sol2.py 用"计算宫号"取代"遍历宫"消掉这一层。
        '''
        # 1) 查 9 行: 每行一个 set
        for r in range(9):
            seen = set()
            for c in range(9):
                v = board[r][c]
                if v == '.':          # '.' 必须在记账**之前**跳过,
                    continue          # 否则 9 个 '.' 会在同一行里"重复"
                if v in seen:
                    return False
                seen.add(v)

        # 2) 查 9 列: 和上面对称, 只是 r/c 互换
        for c in range(9):
            seen = set()
            for r in range(9):
                v = board[r][c]
                if v == '.':
                    continue
                if v in seen:
                    return False
                seen.add(v)

        # 3) 查 9 宫: 外两层定位宫的左上角, 内两层遍历宫内 3x3
        for br in range(0, 9, 3):             # 宫左上角行号: 0, 3, 6
            for bc in range(0, 9, 3):         # 宫左上角列号: 0, 3, 6
                seen = set()
                for r in range(br, br + 3):   # <- 四层嵌套, 这版最丑的地方
                    for c in range(bc, bc + 3):
                        v = board[r][c]
                        if v == '.':
                            continue
                        if v in seen:
                            return False
                        seen.add(v)

        return True                            # 27 组都没冲突

        '''
        Dry Run: 官方 Example 2 (左上角 '5' 改成 '8')
        改动后盘面里有两处 '8' 相撞:
            列冲突: board[0][0]='8' 和 board[3][0]='8'  都在第 0 列
            宫冲突: board[0][0]='8' 和 board[2][2]='8'  都在第 0 宫 (行0-2, 列0-2)
        (官方解释举的是宫; 两处任一被发现都足以 return False)
        本版的执行顺序:
        1) 查行: 行 0 = 8,3,7 无重复 -> 过; 9 行都过
        2) 查列: 列 0 收集到 8('.'跳过)、6、8 -> 第二个 '8' in seen -> return False
           本版列查在宫查之前, 所以在列这一步就返回了, 根本没走到第 3 段。

        Test Cases: 见 sol2.py 文末 (两版共用同一组用例, 已对拍一致)
        '''
