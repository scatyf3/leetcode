# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        res = ListNode()
        tail =  res
        # push k head note from list into heap
        h = []
        for k, head in enumerate(lists):     # k = 第几个链表, head = 那个链表的头
            if head:                         # 空链表要跳过, 否则 head.val 直接 AttributeError
                heapq.heappush(h, (head.val, k, head))
        while len(h)!=0:
            val, k, node = heapq.heappop(h)
            if node.next is not None:
                heapq.heappush(h, (node.next.val, k, node.next))
            tail.next=node
            node.next=None
            tail=tail.next
        return res.next

        '''
        最小堆 k 路归并。O(N log k) 时间 / O(k) 空间  (N = 总节点数, k = 链表条数)
        对拍结论: 正确(7 个固定用例 + 2000 组随机, 全过)。
        实测 k=1000 条 x 100 节点 (N=1e5): 0.049s。
        堆里任何时刻最多 k 个元素 —— 每条链只占一个坑, 弹一个才补一个, 所以是 log k 不是 log N。
        (本地跑要 import heapq; LeetCode 的判题环境已经预导入。)

        --- 核心: 入堆的三元组为什么要塞一个 k ---
            heapq.heappush(h, (head.val, k, head))
                               ↑        ↑  ↑
                          比大小用  打平局用  才是真正要拿回来的东西
        元组比较是**逐位**的: val 相等时 Python 会接着比第二位。
        如果只写 (val, node), 一旦两条链的当前值相同, 就会去比两个 ListNode:
            TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'
        因为 ListNode 没有定义 __lt__。而样例 [[1,4,5],[1,3,4],[2,6]] 正好有两个 1,
        所以这不是边界情况, 是一提交就挂。
        k 是链表编号, 互不相同 => 第二位一定能分出胜负 => 永远比不到第三位的 node。
        任何"唯一且可比较"的东西都行(自增计数器 i 也可以), k 只是顺手。

        通用结论: **往堆里塞不可比较的对象时, 中间垫一个唯一的 tiebreaker。**
        另一种写法是给 ListNode 挂 __lt__:
            ListNode.__lt__ = lambda a, b: a.val < b.val

        --- 踩过的两个坑(互相掩盖) ---
        1. 补货时压回去的是 node 而不是 node.next:
             heappush(h, (node.next.val, k, node))     # ❌ 键取了下一个节点的值, 塞的却是当前节点
           键和值对不上 => 同一个 node 被弹出两次 => 第二次时 tail 恰好就是它,
           tail.next = node 变成自环, 再被 node.next = None 清掉, tail = tail.next 就成了 None,
           下一轮 tail.next = node 崩在 AttributeError。
           报错报在下游, 病根在上游 —— 指针题基本都这样。
        2. res 一个变量同时当哨兵和尾指针:
             res = res.next            # 哨兵丢了
             return res.next           # 返回最后一个节点的 next = None
           哨兵和尾指针必须是两个变量: res 永远不动, tail 负责移动, 最后 return res.next。
        只修 2 不修 1 会静默漏数据([1,2]); 只删 node.next=None 不修 1 会变成死循环。

        --- node.next = None 是多余的(留着不错) ---
        下一轮的 tail.next = 新node 会覆盖它; 而最后一个弹出的节点, 它的 next 本来就是 None
        (因为弹出时若 next 存在就会被压进堆, 那这轮就不是最后一轮)。
        不变式: dummy..tail 这段已定稿, tail.next 是"未定义", 允许脏 —— 每轮都会被写。
        要手动断开的场景是"截断链表"(LC148 从中点切开、LC61、LC86), 不是这种"覆盖指针"。

        Dry Run: lists = [[1,4],[1,3],[2]]
          初始入堆: [(1,0,node1a), (1,1,node1b), (2,2,node2)]   <- 两个 1 靠 k=0/1 分开
          弹(1,0): 压 (4,0,·); 接上 1
          弹(1,1): 压 (3,1,·); 接上 1
          弹(2,2): 无 next;    接上 2
          弹(3,1): 无 next;    接上 3
          弹(4,0): 无 next;    接上 4     堆空退出
          return 1->1->2->3->4

        Test Cases:
        [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]
        []                      -> None      lists 本身为空
        [[]]                    -> None      唯一的链表是空的 <- if head 挡住
        [[],[1],[]]             -> [1]       空链表夹在中间
        [[1]]                   -> [1]
        [[-2,-1],[-3]]          -> [-3,-2,-1]  负数
        [[1,1,1],[1,1]]         -> [1,1,1,1,1]  全相同 <- 没有 k 的话这里必炸 TypeError

        下一步: sol2.py 分治两两合并, 复用 LC21, 同样 O(N log k) 但不需要堆, 空间 O(log k)。
        '''
