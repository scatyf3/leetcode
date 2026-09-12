# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        cur_deque=deque()
        next_deque=deque()

        cur_deque.append(root)

        res=[]
        cur_level=[]

        if root is None:
            return []

        while len(cur_deque)!=0 or len(next_deque)!=0:
            #print("cur")
            ##print(cur_deque)
            #print("next")
            #print(next_deque)
            cur_node=cur_deque.popleft() # append和pop和array一样，只有 popleft是deque独有的
            #print(cur_node)
            cur_level.append(cur_node.val)
            if cur_node.left is not None: #崩在下一轮
                next_deque.append(cur_node.left)
            if cur_node.right is not None:
                next_deque.append(cur_node.right)
            if len(cur_deque)==0 and len(next_deque)!=0:
                res.append(cur_level)
                cur_level=[]
                tmp=cur_deque
                cur_deque=next_deque
                next_deque=tmp # swap2 deque
        res.append(cur_level) # 最后一层退出条件
        
        return res


        