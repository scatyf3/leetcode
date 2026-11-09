"""
# Definition for a QuadTree node.
class Node:
    def __init__(self, val, isLeaf, topLeft, topRight, bottomLeft, bottomRight):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
"""

class Solution:
    def construct(self, grid: List[List[int]]) -> 'Node':
        def all_eq(row_start,row_end,col_start,col_end):
            elem = grid[row_start][col_start]
            for row in range(row_start,row_end+1):
                for col in range(col_start,col_end+1):
                    if grid[row][col]!=elem:
                        return False
            return True
        # advanced version of tree contruction
        def dfs(row_start,row_end,col_start,col_end): # is end closed
            if row_start>row_end and col_start>col_end:
                return None
            if all_eq(row_start,row_end,col_start,col_end): # is leaf, end recursion
                return Node(grid[row_start][col_start],1,None,None,None,None)
            # not all eq, divide
            cur_node = Node(1,0,None,None,None,None)
            row_mid = (row_start+row_end)//2 # n=2**k
            col_mid = (col_start+col_end)//2 # n=2**k
            cur_node.topLeft = dfs(row_start,row_mid,col_start,col_mid)
            cur_node.topRight = dfs(row_start,row_mid,col_mid+1,col_end)
            cur_node.bottomLeft = dfs(row_mid+1,row_end,col_start,col_mid)
            cur_node.bottomRight = dfs(row_mid+1,row_end,col_mid+1,col_end)
            return cur_node
        n=len(grid)-1
        res = dfs(0,n,0,n)
        # print(res)
        return res