`preorder[pre_l]` 是根；在 inorder 里找到根的下标 `idx`（哈希表预存，O(1)），`left_size = idx - in_l`，再按 `left_size` 把 preorder 切成左右两段递归。区间全用左闭右开，`pre_l >= pre_r` 返回 None。

⚠ preorder 的切分只能靠 `left_size` 算：左子树 `[pre_l+1, pre_l+1+left_size)`，右子树 `[pre_l+1+left_size, pre_r)`。两个数组的右段起点只有第一层才对得上。
