class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:
        '''
        there has to be a gap of at least n intervals between two tasks with the same label.
        minimum number of CPU intervals required to complete all tasks.

        1. we only consider the bottleneck, aka the max count element
        2. max cnt x n+num elem(lauch overhead)
        '''
        cnt = Counter(tasks)
        max_cnt = max(cnt.values())
        # 尾巴上站着的只有并列最多的那几种
        num_max = sum(1 for v in cnt.values() if v == max_cnt)
        # 第一项：骨架下界；第二项：块塞满后无空闲，长度就是任务数
        return max((max_cnt - 1) * (n + 1) + num_max, len(tasks))