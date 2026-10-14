# 347. Top K Frequent Elements

1. 一眼heap，先用counter构造elem - freq，然后用freq做key来搞heap
2. python heap sytax, and python只有min heap max的话要手动用负号


然而这里存在问题
现状复杂度：设 n = len(nums)，m = 不同元素个数（最坏 m = n）。

1. 建 Counter：O(n)
2. 把 m 个元素全部推进堆：O(m log m) ← 瓶颈在这里
3. 弹 k 次：O(k log m)

小处（直接说，不算剧透）
1. Counter() + 手动循环可以直接写成 Counter(nums)，它内部是 C 实现的计数。
2. 迭代时用 for key, freq in cnt.items()，省掉 m 次哈希查找。

agent hint：
反过来想：维护一个 大小恒为 k 的最小堆（按频次，不取负）。每来一个新元素就 push，堆超过 k 就 pop 掉堆顶——堆顶是当前 k+1 个里频次最小的，它不可能是答案。这样每次操作是 log k 而不是 log m。

但感觉没区别啊，还是要过m个元素，只是不push只pop，这里的复杂度是？	O(m log m) => O(m log k)

还有一个另外个O(n)的思路是啥，hint下？
线性时间的钥匙藏在这句话里：堆和排序都是"比较"出来的，而比较排序的下界就是 O(m log m)。想突破它，就得找到某个不靠比较的结构性性质。
1. 凡是"key 是有界整数"，就有不比较的排序法可用。想想哪一类。
2. 你的 Counter 是 元素 → 频次。现在把这张表反过来：频次 → 有这个频次的元素列表


桶排序的桶是什么？
`buckets[freq] = [所有出现了 freq 次的元素]`

不是hash，因为要求key天生有序: 
{3:[1], 2:[2], 1:[3]} 存的信息完全一样。但桶排序要的不只是"存"，是**"排"**——数组下标天然从小到大排好了，你 for freq in range(n, 0, -1) 倒着走一遍，就等于按频次从高到低把元素扫出来了。顺序是数组下标白送的，一次比较都没做。 dict 做不到这件事。

这为啥能skip排序，这不是还是排序了吗？
输出确实是有序的，但我们一次比较都没做。

用迭代取代了排序，like，一个元素在bucket里面见到一次，就向高index挪一次对吗？
都一样，sol写的是建counter再建桶

wait，还是要建counter，然后再基于counter建桶对吗，两个O(n) pass?
对的

其实heap用一个guard也能做到线性复杂度，并非
带守卫的堆不是线性的，它是"期望线性"，最坏仍然是 O(m log k)。 桶排序才是最坏情况下也保证 O(n)。

这里heap or not的决策因为啥，因为prior knowledge知道count的取值范围，所以不用heap，用indexing取代比较了吗
对的
