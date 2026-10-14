class Solution:
    def letterCombinations(self, digits: str) -> list[str]:
        cur = []
        res = []
        mp = {
            "2": ["a","b","c"],
            "3": ["d","e","f"],
            "4": ["g","h","i"],
            "5": ["j","k","l"],
            "6": ["m","n","o"],
            "7": ["p","q","r","s"],
            "8": ["t","u","v"],
            "9": ["w","x","y","z"],
        }

        def dfs(cur_pos):
            if cur_pos==len(digits):
                res.append("".join(cur) )
                return 
            cur_lst = mp[digits[cur_pos]]
            for num in cur_lst:
                cur.append(num)
                dfs(cur_pos+1)
                cur.pop()
        dfs(0)
        return res
            
        