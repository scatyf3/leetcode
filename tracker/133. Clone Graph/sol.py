from typing import Optional
class Solution:
    def cloneGraph(self, node: 'Node') -> 'Node':
        '''
        1. 和random linkedlist一样，hash维护old -> new的映射
        2. 但不一样的是，如何保证old全都被iterate，之前linkedlist的结构保证，然而graph需要dfs
        3. 记得第二趟更新neigh用新的node而不是老node
        '''
        mp = {}
        if node is None: #edge case
            return None
        def bfs(start):
            q = deque()
            q.append(start)
            visited = set()
            visited.add(start)
            while len(q)!=0:
                len_q=len(q)
                for _ in range(len_q):
                    cur_node = q.popleft()
                    new_node = Node(cur_node.val,None)
                    mp[cur_node]=new_node
                    for neigh in cur_node.neighbors:
                        if neigh is not None and neigh not in visited:
                            q.append(neigh)
                            visited.add(neigh)
        bfs(node)
        for old_node in mp:
            new_node=mp[old_node]
            for neigh in old_node.neighbors:
                new_node.neighbors.append(mp[neigh]) # for neigh, append newer version
        return mp[node]
                    