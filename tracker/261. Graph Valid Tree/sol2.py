class Solution:
    def validTree(self, n: int, edges: list[list[int]]) -> bool:
        # union find
        # merge set together via array indexing
        union_find = [i for i in range(n)]
        for edge in edges:
            # check if egde0 and edge 1 is connected
            # how to check cheaply
            # print(union_find)
            if union_find[edge[0]]==union_find[edge[1]]:
                return False
            # if not, add to connected via iteration
            to_replace=union_find[edge[1]] #save, else it will change during iteration
            to_merge=union_find[edge[0]]
            for idx,val in enumerate(union_find):
                if val==to_replace:
                    union_find[idx]=to_merge
        # check all eq
        print(union_find)
        st = set(union_find)
        if len(st)>1:
            return False
        else:
            return True
        
