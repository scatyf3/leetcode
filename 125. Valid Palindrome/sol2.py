class Solution:
    def isPalindrome(self, s: str) -> bool:
        '''
        解法2: 原地双指针, O(n) 时间 / O(1) 额外空间

        和 sol.py 的区别只有一处: **不预处理**。
        sol.py 先把整串洗干净(列表推导 + join)再比, 洗出来的新串长度和 s 同阶
        -> O(n) 额外空间。这里改成"边走边跳", 遇到非字母数字就把指针挪过去,
        全程只有 l / r 两个整数, 额外空间 O(1)。

        骨架: 外层管"配对比较", 内层两个 while 管"把指针推到下一个有效字符"。
        '''
        l, r = 0, len(s) - 1

        while l < r:
            while l < r and not s[l].isalnum():   # 左指针右移, 跳过标点/空格
                l += 1
            while l < r and not s[r].isalnum():   # 右指针左移, 同理
                r -= 1

            if s[l].lower() != s[r].lower():      # lower() 推迟到比较这一刻才调
                return False

            l += 1                                # 这对比完了, 两边同时收缩
            r -= 1

        return True

        '''
        三个容易写错的点:

        1) 内层 while 的 `l < r` 守卫不能省
           写成 `while not s[l].isalnum(): l += 1` 的话, 输入 ".,"(全是标点)
           时 l 会一路冲出右边界 -> IndexError。守卫让它最坏停在 r 上。

        2) lower() 别提前对整串调
           `s = s.lower()` 会新建一个长度 n 的字符串 —— O(1) 空间就白折腾了。
           str 不可变, 所有"改"都是造新对象, 这题里能省则省。
           c.lower() 只造一个单字符, 常数大小, 不影响复杂度。

        3) isalnum() 不是 isalpha()
           题目要的是"字母和数字", 数字也算。用 isalpha() 会把数字一起扔掉:
           s = "0P"  ->  isalpha 版洗成 "p" -> 判成 True(错, 应为 False)
           这个 case LeetCode 就在样例里, sol.py 那版过不了。

        外层 `l < r` 还是 `l <= r` 都对: l == r 时是同一个字符跟自己比, 恒等,
        多跑一轮而已。习惯写 `l < r`, 省掉那次无意义的比较。

        Dry Run: s = "A man, a plan"[:8] 取 "A man, a"
          下标:    0=A 1=' ' 2=m 3=a 4=n 5=',' 6=' ' 7=a
          l=0,r=7: 都已是 alnum -> 'a' vs 'a' 相等 -> l=1, r=6
          l=1,r=6: s[1]=' ' 跳到 l=2; s[6]=' ' 跳到 r=5, s[5]=',' 再跳到 r=4
                   -> s[2]='m' vs s[4]='n' -> 不等 -> False

        复杂度: l 和 r 各自单向移动, 合起来最多走完 n 格 -> O(n)。
        内层 while 是嵌套的, 但不是 O(n^2) —— 判断循环复杂度看的是"指针总位移",
        不是"循环嵌了几层"。
        '''
