# 105. Construct Binary Tree from Preorder and Inorder Traversal

given两个array
1. 从preorder切分出root
2. inorder根据root的value，找到其对应的root index，然后切分左右tree的list
3. 根据左右tree list的len，在preorder里切分左右

我们忘记了第三步，只有刚开始的时候，pre/in的right start相等，后面就不好说了

传参：两个list的左右指针，两个list