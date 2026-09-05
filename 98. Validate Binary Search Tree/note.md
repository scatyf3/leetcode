
我想了一个局部比较，但是二叉搜索树要求root>left max，小于right min对吗

然后dfs里维护用参数left max和right min，return t/f即可，还不对，这和当前的sol不一致

两个办法
1. 维护祖先区间，left.val必定小于祖先区间，right.val大于祖先区间
2. 返回left max和right min，return t/f即可，当前node必须大于lmax小于rmin

