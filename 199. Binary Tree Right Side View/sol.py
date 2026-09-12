# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        res = []
        q_cur = deque([root]) # naive array used as stask
        q_nxt = deque([])
        qlen=1
        if root is None:
            return res
        while len(q_cur)!=0:
            new_qlen=0
            lastest_node_val=-1
            for i in range(qlen):
                cur_node=q_cur.popleft()
                if cur_node.left is not None:
                    q_nxt.append(cur_node.left)
                    new_qlen+=1
                if cur_node.right is not None: 
                    q_nxt.append(cur_node.right)
                    new_qlen+=1
                lastest_node_val = cur_node.val
            res.append(lastest_node_val)
            qlen=new_qlen
            new_qlen=0
            q_cur=q_nxt
            q_nxt=deque([])
        return res
