# 150. Evaluate Reverse Polish Notation

草这不是编译吗，我最爱的。。。

但是全是语法的坑
1. if - **elif** - else，否则else只和第一个if配对
2. 记得转int
3. //并非向0取整而是向下，比如-7//2=-4，向0取证用int(a/b)

然后还有个操作数问题，应该是num2-num1，因为后出栈的在前