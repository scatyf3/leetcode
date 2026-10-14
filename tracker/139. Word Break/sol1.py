class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        # for each word in wordDict, process str to get the possible slice
        # globally, see if these slice can be cover full str
        # agent: last step we can use hashtable/graph
        # build the graph
        valid_slice = {}
        for word in wordDict:
            for start_idx in range(len(s)):
                iter_idx = start_idx
                while iter_idx<len(s) and iter_idx-start_idx<len(word) and s[iter_idx]==word[iter_idx-start_idx]:
                    # print(iter_idx)
                    iter_idx+=1
                if iter_idx-start_idx == len(word):
                    if start_idx not in valid_slice: 
                        # we can't use valid_slice[start_idx] not Nont
                        valid_slice[start_idx] = [iter_idx]
                    else:
                        valid_slice[start_idx].append(iter_idx)
                        
        next_visit = [0]
        visited = set()
        while len(next_visit)!=0:
            curr_idx = next_visit.pop()
            visited.add(curr_idx)
            if(curr_idx==len(s)): # len(s) means end althought it is not valid index
                return True
            if(curr_idx in valid_slice):
                for next_idx in valid_slice[curr_idx]:
                    if next_idx not in visited:
                        next_visit.append(next_idx)
        return False

        '''
        我的第一版(naive)。建图 + DFS 可达性。
        对拍结论: 正确(8 个固定用例 + 3000 组随机 vs 标准 DP, 零反例)。
        复杂度: 建图 O(n * m * L), 遍历 O(V + E) = O(n + n*m)  => 总体 O(n * m * L)
                空间 O(n * m)  (n = len(s), m = 词数, L = 最长词长)
        实测最坏形状 s = "a"*300 + "b", dict = ["a","aa",...,"a"*10]: 0.0015s

        思路两段式(这是我自己想出来的框架, 事后发现就是标准解的图论说法):
          1. 对每个词, 找出它在 s 里的所有出现位置 -> 每个位置产生一条边
          2. 看这些片段能否首尾相接地铺满整串 -> 从 0 能否走到 n 的可达性问题

        关键: 节点是"缝"不是字符, 一共 n+1 个 (0..n)。
        curr_idx == len(s) 表示走到了最后一条缝 = 整串切完, 它不是合法字符下标。
        边只向右 (i -> i+len(word)), 所以图是 DAG, 无环, 不会死循环;
        visited 是为了不重复展开同一个切点(不是防环), 保证每个节点最多出栈一次。

        踩过的两个坑:
        1. KeyError: 0
           写成 if valid_slice[start_idx] is not None —— Python 取不存在的键是**抛异常**,
           不是返回 None(和 JS 的 undefined 不同)。要用 `start_idx not in valid_slice` 判断,
           或 defaultdict(list) / setdefault。
        2. if iter_idx == len(word)   <- 下标和长度混用
           iter_idx 是 s 里的**绝对下标**, len(word) 是**长度**, 只有 start_idx == 0 时碰巧相等。
           正确是 iter_idx - start_idx == len(word) ("走了多少步" == 词长)。
           只修坑 1 不修坑 2 的话, "leetcode" 会返回 False —— 坑 1 把坑 2 挡住了。
           自查: 代 start_idx=3, word="code", 匹配成功时 iter_idx=7 而 len(word)=4, 一眼就崩。
           => notes/off-by-one-checklist.md 的「这个数值指的是位置还是长度?」第三次出现。

        可以更短的地方(不影响正确性):
          - 内层 while 那 4 行 = s.startswith(word, start_idx), 内置自带越界处理
          - valid_slice[start_idx] = [iter_idx] / else append  =>  setdefault(start_idx, []).append(...)
          - 边只向右, 所以其实不用 DFS + visited, 从左到右扫一遍 reach[] 即可(见 sol2.py)

        Dry Run: s = "leetcode", wordDict = ["leet", "code"]
          建图: "leet" 在 0 处匹配 -> 0 -> 4 ; "code" 在 4 处匹配 -> 4 -> 8
                valid_slice = {0: [4], 4: [8]}
          遍历: 栈[0] -> 弹 0, 不是 8, 压 4
                栈[4] -> 弹 4, 不是 8, 压 8
                栈[8] -> 弹 8 == len(s) -> True

        Test Cases:
        "leetcode",      ["leet","code"]                    -> True
        "applepenapple", ["apple","pen"]                    -> True   词可重复使用
        "catsandog",     ["cats","dog","sand","and","cat"]  -> False  经典反例: 贪心切会掉坑
        "abcd",          ["a","abc","b","cd"]               -> True   贪心切最长会 FAIL, 必须能回退
        "cars",          ["car","ca","rs"]                  -> True
        "a",             ["b"]                              -> False
        "ab",            ["a"]                              -> False  只能覆盖一半
        '''
