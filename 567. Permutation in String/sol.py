# 第一版尝试, 没通过。一个设计问题 + 若干实现问题:
#
# 设计问题(根子): 让 need 在计数归零时 del 掉键, 用 len(need)==0 当判定。
#   a. 滑动窗口的"进"和"出"必须是一对**逆操作**, 而 del 是破坏性、不可逆的。
#      字符移出窗口时 need 里已经没这个键, `if s2[l] in need` 恒 False, 需求恢复不回来。
#      反例 s1="abc" s2="abxc": 窗口滑到 "bxc" 时 need 已空 -> 假阳性 True(正确答案 False)。
#      随机对拍 20000 组错 925 组。
#   b. 本质是在用容器的 size 隐式编码状态量, 逼着自己为了把 size 压到 0 去破坏数据本身。
#      原则: 别用容器的 size / 键的存在性表达状态, 状态就显式存一个 int。
#
# 实现问题:
#   1. Counter 是 dict, 没有 .remove() -> AttributeError。删键要用 del need[c]
#   2. `if need[s2[i]]==0` 写在 `if s2[i] in need` 的**块外**: s1 里没有的字符
#      读出来是 0(Counter 缺失键返回 0 且不插入), 条件成立 -> del 不存在的键 -> KeyError
#   3. 滑动循环里加减方向和初始化循环相反: 右进写成 +=1、左出写成 -=1, 应该反过来
#      (统一为: 进字符 -> 需求减, 出字符 -> 需求加)
#   4. len(s1) > len(s2) 时初始化循环 range(s1len) 直接越界, 开头没挡
#   5. 残留 print
#
# 修正版见 sol2.py。
from collections import Counter

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        '''
        双指针+counter，枚举右，invalid收缩左，可以快速收缩或者l+=1

        agent：我混了两种，定长窗口和高级

        naive定长扫描，l-r+，每次检查窗口里是否valid

        检查窗口里是否valid的操作怎么做，hash吗，其实可以小数组, copy+如果全0。
        那这个复杂度全都在这个小数组上了吗，感觉比较辅料

        搞个need的set即可
        '''
        s1len=len(s1)
        s2len=len(s2)
        need = Counter()
        for c in s1:
            need[c]+=1
        # check counter
        for i in range(s1len):
            if s2[i] in need:
                need[s2[i]]-=1
            if need[s2[i]]==0:
                need.remove(s2[i])
        if len(need)==0:
            return True
        print(need)
        l = 0
        r = s1len # first invalid
        while r<s2len:
            if s2[r] in need: # 忽略和s1 need无关的东西
                need[s2[r]]+=1
            if s2[l] in need:
                need[s2[l]]-=1
            if need[s2[l]]==0:
                need.remove(s2[l])
            if len(need)==0:
                return True
            print(need)
            r+=1
            l+=1
        return False
