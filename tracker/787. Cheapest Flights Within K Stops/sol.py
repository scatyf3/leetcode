class Solution:
    def findCheapestPrice(self, n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
        # bfs 探测从src走k步reachable，path及其cost，然后检查dst是否在其中，
        # 如果在的话，最小的是什么（直接bfs的时候动态update最小，以防explicit存多个路径）
        # talk with agent: visited直接用最小cost呗，然后一个path update下cost即可

        cost_table = {}
        flight_table = {} # src => [(dst,cost)]
        for isrc,idst,cost in flights: # do not use src and dst, it will override input
            if isrc in flight_table:
                flight_table[isrc].append((idst,cost))
            else:
                flight_table[isrc]=[(idst,cost)]
        # print(flight_table)
        # {0: [(1, 100)], 1: [(2, 100), (3, 600)], 2: [(0, 100), (3, 200)]}
        q = deque([(src,0)])
        cost_table[src]=0
        cnt = k+1
        while cnt>0 and q:
            q_len = len(q)
            for _ in range(q_len):
                cur_node,cur_cost = q.popleft()
                # accumulate cost
                if cur_node in flight_table:
                    for cur_dst,cost in flight_table[cur_node]:
                        if cur_dst in cost_table and cur_cost+cost<cost_table[cur_dst]:  
                            # should the cost less than current to be inqueue?
                            cost_table[cur_dst]=min(cost_table[cur_dst],cur_cost+cost)
                            q.append((cur_dst, cur_cost+cost))
                        if cur_dst not in cost_table:
                            cost_table[cur_dst]=cur_cost+cost
                            q.append((cur_dst, cur_cost+cost))
                    # print(cost_table)
            cnt-=1
            
        if dst in cost_table:
            return cost_table[dst]
        else:
            return -1

