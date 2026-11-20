# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def minCameraCover(self, root: Optional[TreeNode]) -> int:
        NEED, CAM, COVERED = 0, 1, 2
        ans = 0

        def dfs(node):
            nonlocal ans
            if not node:
                return COVERED             # 空节点报什么？
            l, r = dfs(node.left), dfs(node.right)

            if l is NEED or r is NEED:    # 什么情况下被逼着装？
                ans += 1
                return CAM
            if l is CAM or r is CAM:       # 什么情况下我已经被盖住了？
                return COVERED
            return NEED                  # 剩下的情况

        if dfs(root) is NEED:            # 根的收尾
            ans += 1
        return ans
