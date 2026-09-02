# 424. Longest Repeating Character Replacement

滑动窗口，但是起始状态如何思考？
l=r=0

维护hashmap当counter，额外维护max letter是谁，需要的操作k

agent：不需要max letter，只需要max count？

那这里维护方法是不是有个easy的题里的方法，通过数学抵消，用很简单的加减法就能压缩？

agent：169里的 摩尔投票，但用不了
1. 它给的是「谁」，不是「几个」。 摩尔投票返回候选者，不返回它的次数 —— 而 424 的判定式 (r-l+1) - mx <= k 要的恰恰是那个次数。想拿次数还得再扫一遍。
2. 它要求「众数超过一半」这个前提。 169 题面白纸黑字保证了 majority 存在。424 的窗口里完全可能没有过半的字符（"ABC"，最大频次 1，远不到一半），这时摩尔投票的候选者是任意的垃圾值，不是最大频次那个。
3. 最致命的：它不可逆。 滑窗需要 remove(arr[l]) —— 从左边撤销一个元素。摩尔投票的状态 (candidate, count) 是一路抵消压出来的，抵消掉的信息已经丢了，撤不回来。count -= 1 根本没有意义，你不知道当初是谁跟谁抵消的。

然后r移动，每一步都判断是否valid，如果valid则 继续，如果不valid，则【收缩左边一格，然后重新判断，直到合法】

为啥不是reset l==r，不过好像也make sense，直接reset会skip一些东西。

那怎么在不知道max letter的情况下维护max count？ 

思考，max(cnt val)还是隐式的max elem啊，而且好像还不如存max elem，因为这样 max(cnt.val) 并非免费？
存max elem也一样的，用max elem查count，而且维护max elem还骂发明

cnt.val是个list，list max相当于O(n)吗，然后total复杂度是O(n^2)。不对，字母是const，这无所谓

真正能做到 O(1) 的是另一种存法：存「频次的频次」。 不记谁最大，记「有几个字母的计数是 1、有几个是 2、……」，这样啥操作都是O(1)

### 语法上

naive hash好像要分类讨论key在不在，首先这个写法是「key not in dict」而不是 「key is not in dict」

```
if l not in cnt:
    cnt[s[l]]=1
else:
    cnt[s[l]]+=1
```

其次，用Counter可以skip这个判断，Counter 缺失键默认返回 0，有些等价写法
```
cnt = Counter();          cnt[x] += 1            # ← 最短
cnt = defaultdict(int);   cnt[x] += 1            # 一样
cnt = {};                 cnt[x] = cnt.get(x, 0) + 1   # 纯 dict 的标准写法
```

所以这里 cnt.get(x, 0)是啥意思？
d.get(键, 默认值) = 「取这个键的值；表里没有就返回默认值，而不是报错」。

感觉是个好东西，可以代替我那个if else对吗？

lc里大部分key=>int的dict都可以写counter对吗? 不对，只有真的字面意义是计数的时候再用

```
坑 1: 减到 0 不删键 —— len() 会骗你
  cnt = Counter({'B': 1, 'A': 0})  len = 2  <- 窗口里其实只剩 1 种字符, len 却是 2
  正确数法: 1

坑 2: 减法丢掉非正数
  a - b        = Counter({'A': 1})   <- B 的 -2 被扔了, 不是数学减法
  a.subtract(b)= Counter({'A': 1, 'B': -2})   <- 想要负数得用这个(原地改)

坑 3: 读缺失键不报错, 静悄悄给 0
  d['zzz'] = 0  而普通 dict 会 KeyError —— 打错 key 时不会被发现
  读完之后 d = Counter()  <- 只读不写, 键没被插进去(和 defaultdict 不同)
  普通 dict: KeyError
```

### 写法

有两个写法，然而里面有两个写法
1. 外层循环肯定iterate left boundary, while valid，继续扩有边界
2. 外层循环肯定iterate right boundary,while not valid，l默认为0，缩左边界

这里写法取舍是啥，很直觉的双指针是1，然而1有好多edgecase和+-1，写2更简略，怎么判断写2更简略？
判据是循环退出后的后置条件，是不是一个单一命题。
1. case 1 退出时是第一个invalid
2. case 2 退出时是第一个valid

形状 2 退出后你确切知道窗口是合法的，所以结算就是 r - l + 1，不加不减。形状 1 退出后你不知道是哪种情况停的 —— 而这两种情况的结算方式不一样（多扩一格 vs 没多扩）。你上一版那个 -1 就死在这儿：它默认了「一定是 valid 失败停的」，遇到 AAAA 撞边界停的就削错了。

case2 的不变式只有一句：「结算的那一刻，窗口 [l, r] 一定合法」

> wok有agent好幸福，我这种钻牛角尖的问题都会有回答。

有任何左右指针，但用case1 的情况吗，还是in general都是case2更好？
默认用 2，但形状 1 有三类不可替代的场景。
1. 需要每个左端点各自答案而不是全局最优
2. 不支持删除，聚合没有逆运算，max min等
3. 删除很贵

双指针决策
```
1. 两个指针同向还是相向?          相向 -> 另一族, 到此为止
2. 答案是一个数还是一个数组?      数组 -> 形状 1
3. state 支持"删一个"吗?          不支持 -> 形状 1 或换数据结构(单调队列)
4. 删除很贵吗?                    很贵 -> 形状 1 + 二分
   以上都不是                    -> 形状 2
```