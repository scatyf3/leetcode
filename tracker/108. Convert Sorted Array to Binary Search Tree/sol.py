# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def sortedArrayToBST(self, nums: list[int]) -> TreeNode | None:
        '''
        A height-balanced binary tree is a binary tree in which the depth of the two subtrees of every node never differs by more than one.
        从中间分开元素吧
        '''

        def dfs(left,right):
            if left>right:
                return None
            mid = (left+right)//2
            mid_val = nums[mid]
            cur_node = TreeNode(mid_val)
            ll = left
            lr = mid-1
            rl = mid+1
            rr = right
            cur_node.left = dfs(ll,lr)
            cur_node.right = dfs(rl,rr)
            return cur_node
        return dfs(0,len(nums)-1)

        