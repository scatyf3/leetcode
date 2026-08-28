class Solution:
    def countSubstrings(self, s: str) -> int:
        # single center
        n=len(s) # eg n = 3
        counter=0
        for i in range(0,n): # [1,2)
            l=r=i
            while(l>=0 and r<n and s[l]==s[r]):
                counter+=1
                l-=1
                r+=1
        for i in range(0,n-1): # [0,2) 0 and 1
            l=i
            r=i+1
            while(l>=0 and r<n and s[l]==s[r]):
                counter+=1
                l-=1
                r+=1
        return counter

        '''
        我的第一版, 一次过。中心扩展 O(n^2) 时间 / O(1) 空间。
        对拍结论: 正确, 无 bug (退化用例 + 3000 组随机全过)。
        LC5 之后第一次写回文, 骨架直接迁过来了, 只把"取最长"换成"每扩成功一次 counter += 1"。

        两个循环分别枚举:
          第一个 for: n 个奇中心   (l = r = i,     轴是字符 s[i])
          第二个 for: n-1 个偶中心 (l = i, r = i+1, 轴是 s[i] 和 s[i+1] 之间的缝)

        和重构版 sol2.py 的差别只有两点(都不是正确性问题, 见 note.md):
          1. 两个循环体一字不差 -> 可以抽成 expand(l, r) 调两次
          2. range(0, n-1) 的上界不用特意算: 偶中心传 (n-1, n) 时 r < n 首轮就假, 自然返回 0
        '''
