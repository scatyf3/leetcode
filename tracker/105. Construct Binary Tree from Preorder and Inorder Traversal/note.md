# 105. Construct Binary Tree from Preorder and Inorder Traversal

## pass3

```python
class Solution:
    def buildTree(self, preorder: list[int], inorder: list[int]) -> TreeNode | None:
        def dfs(prel,prer,inl,inr):
            if prer<prel or inr<inl:
                return None
            root = preorder[prel]
            in_root_index=inl
            left_len=0
            while inorder[in_root_index]!=root:
                in_root_index+=1
                left_len+=1
            left_node = dfs(prel+1,prel+1+left_len-1,inl,in_root_index-1)
            right_node = dfs(prel+1+left_len-1+1,prer,in_root_index+1,inr)

            root_node = TreeNode(root,left_node,right_node)
            return root_node
        return dfs(0,len(preorder)-1,0,len(inorder)-1)
```

唉这个treelen好麻烦啊


## pass2
为啥edge case是`if pre_l>=pre_r or in_l>=in_r:`，为啥大于等于

一个小东西没转过来，在 [l, r) 下：
1. 区间里的元素是 l, l+1, ..., r-1，一共 r - l 个；
2. l == r 时长度为 0，区间是空的，比如 [1, 1) 里一个元素都没有；
3. 所以 l >= r 就该返回 None。写 >= 而不只写 ==，是为了防御性地兜住 l > r 的情况

## 思路

given两个array
1. 从preorder切分出root
2. inorder根据root的value，找到其对应的root index，然后切分左右tree的list
3. 根据左右tree list的len，在preorder里切分左右

我们忘记了第三步，只有刚开始的时候，pre/in的right start相等，后面就不好说了

传参：两个list的左右指针，两个list