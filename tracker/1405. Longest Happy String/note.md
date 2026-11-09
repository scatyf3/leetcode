# 1405. Longest Happy String


1. 怎么formulate一个greedy问题，只看一步？是的，贪心本来就是每步做一个局部决定。不过这道题真正值得记的，不是"只看一步"，而是把一步缩到最小：一次只放一个字符，需要分类讨论的情况就没有了
2. dict的语法，`for ch in sorted(cnt, key=cnt.get, reverse=True):` 按照value，从大到小迭代key
3. 如果for没被break，可以用for else。或者naive的办法是判断res有没有被变化
4. 怎么理解continue 的语法，换成 if not a and not b，则append - break这对吗，continue是语法糖吗？


continue 做了什么

continue 会跳过本轮循环剩下的代码，直接进入下一轮。所以"if 条件成立就 continue"等价于"把后面的代码都包进 if not 条件里"。几个 continue 叠在一起，就等于把它们的条件取反后用 and 连起来，这正是你写的形式。根据德摩根律，也可以写成 if not (A or B)。

它算不算语法糖

严格说不算，它是一个独立的控制流语句。但在这种用法里，你可以把它理解成一种写法风格，叫 guard clause（卫语句）：先把不符合条件的情况一个个排除掉，剩下的就是主逻辑。