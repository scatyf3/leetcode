class Solution:
    def partition(self, s: str) -> list[list[str]]:
        '''
        ❌
        start from len=1 str，然后不断merge
        有奇merge和偶merge
        dfs直接传merge的list，每次都用sliding windows遍历list，能merge则merge，继续递归...

        agent：一个提示，不涉及具体写法：78 是靠“只能从 start 往后挑”把顺序固定下来的。对一个字符串来说，从左往右做决定时，每一层要决定的“那一件事”是什么？想清楚这个，重复的问题自然就没有了，合并规则也不需要了。
        是否要在这个位置split？

        是不是搞个stack啊
        '''

        res = []
        def is_p(start,end):
            while start<end:
                if s[start]!=s[end]:
                    return False
                start+=1
                end-=1
            return True

        def dfs(start,intervals):
            if start==len(s): 
                # 切完了结算，我们只care切下来的valid
                # 我们不care remain是否valid
                # 然而因为至少可以按单字符串切，肯定到最后是valid的
                cur = []
                for interval in intervals:
                    cur.append(s[interval[0]:interval[1]])
                # but this interval do not consider remaining part...
                res.append(cur)
                return 

            for idx in range(start,len(s)):
                if is_p(start,idx):
                    intervals.append((start,idx+1)) 
                    dfs(idx+1,intervals)
                    intervals.pop()

        dfs(0,[])
        return res