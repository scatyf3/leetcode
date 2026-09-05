from typing import List


class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        rows = [set() for _ in range(9)]
        cols = [set() for _ in range(9)]
        boxes = [set() for _ in range(9)]

        for r in range(9):
            for c in range(9):
                v = board[r][c]
                if v == '.':
                    continue

                b = (r // 3) * 3 + c // 3        # 一行算出宫号, 取代四层嵌套

                # 一个格子记三笔账, 任一处已存在即冲突
                if v in rows[r] or v in cols[c] or v in boxes[b]:
                    return False

                rows[r].add(v)
                cols[c].add(v)
                boxes[b].add(v)

        return True

    def isValidSudokuOneSet(self, board: List[List[str]]) -> bool:
        seen = set()
        for r in range(9):
            for c in range(9):
                v = board[r][c]
                if v == '.':
                    continue
                keys = (('r', r, v), ('c', c, v), ('b', (r // 3) * 3 + c // 3, v))
                if any(key in seen for key in keys):
                    return False
                seen.update(keys)
        return True

