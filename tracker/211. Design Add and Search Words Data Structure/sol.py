
class TrieNode():
    def __init__(self):
        self.nodes={}
        self.is_leaf=False


class WordDictionary:
    # key idea: tries?
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        cur_node = self.root
        for c in word:
            if c not in cur_node.nodes:
               cur_node.nodes[c]=TrieNode()
            cur_node=cur_node.nodes[c]
        cur_node.is_leaf=True 

    def search(self, word: str) -> bool:
        find = False
        def dfs(index,cur_node):
            nonlocal find
            if index==len(word): # edge case is hint by agent
                if cur_node.is_leaf:
                    find=True
                return

            c = word[index]
            if c==".":
                for key in cur_node.nodes: # fanout
                    dfs(index+1,cur_node.nodes[key])
            else:
                if c in cur_node.nodes:
                    dfs(index+1,cur_node.nodes[c])
                else: # break, invalid
                    return

        dfs(0,self.root)
        return find
